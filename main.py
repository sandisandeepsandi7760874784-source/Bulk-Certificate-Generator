from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import time

from . import models, schemas, database, generator

# This creates all the tables in our SQLite database automatically when the app starts
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Bulk Certificate Generator")


def process_bulk_request(bulk_request_id: int):
    """
    Background Task: Processes a bulk request.
    We run this in the background so the user gets an immediate API response
    while the server generates PDFs.
    """
    # Create a new database session strictly for this background task
    db = database.SessionLocal()
    try:
        # Fetch the main request from the database
        bulk_request = db.query(models.BulkRequest).filter(models.BulkRequest.id == bulk_request_id).first()
        if not bulk_request:
            return
        
        # Mark the entire bulk request as PROCESSING
        bulk_request.status = models.StatusEnum.PROCESSING
        db.commit()
        
        all_success = True
        
        # Iterate over every recipient and generate their certificate
        for recipient in bulk_request.recipients:
            recipient.status = models.StatusEnum.PROCESSING
            db.commit()
            
            try:
                # Optional: Sleep for 1 second just to simulate heavy processing (makes testing status checks easier)
                time.sleep(1)
                
                # Clean the name to create a safe file name (remove special characters)
                safe_name = "".join([c for c in recipient.name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                filename = f"cert_req{bulk_request.id}_rec{recipient.id}_{safe_name.replace(' ', '_')}.pdf"
                filepath = os.path.join(generator.CERTIFICATE_DIR, filename)
                
                # Generate the PDF file
                generator.generate_certificate(
                    name=recipient.name, 
                    course_title=bulk_request.title, 
                    output_path=filepath
                )
                
                # If successful, save the file path and update status
                recipient.file_path = filepath
                recipient.status = models.StatusEnum.COMPLETED
                
            except Exception as e:
                # If generation fails, save the error message
                recipient.status = models.StatusEnum.FAILED
                recipient.error_message = str(e)
                all_success = False
                
            db.commit()
            
        # Update the overall status based on whether all certificates succeeded
        if all_success:
            bulk_request.status = models.StatusEnum.COMPLETED
        else:
            bulk_request.status = models.StatusEnum.FAILED
        
        db.commit()
    finally:
        # Always make sure to close the database session
        db.close()


@app.post("/api/requests/", response_model=schemas.BulkRequestResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_bulk_request(
    request_data: schemas.BulkRequestCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(database.get_db)
):
    """
    API Endpoint: Submit a new batch of recipients to generate certificates for.
    """
    # 1. Save the main bulk request to the DB
    db_bulk_request = models.BulkRequest(title=request_data.title)
    db.add(db_bulk_request)
    db.commit()
    db.refresh(db_bulk_request)
    
    # 2. Save each recipient to the DB linked to the bulk request
    for rep in request_data.recipients:
        db_recipient = models.Recipient(
            bulk_request_id=db_bulk_request.id,
            name=rep.name,
            email=rep.email
        )
        db.add(db_recipient)
    db.commit()
    db.refresh(db_bulk_request)
    
    # 3. Tell FastAPI to start our generator function in the background
    background_tasks.add_task(process_bulk_request, db_bulk_request.id)
    
    # 4. Return the newly created request (which is in PENDING state) immediately
    return db_bulk_request


@app.get("/api/requests/{request_id}", response_model=schemas.BulkRequestResponse)
def get_bulk_request_status(request_id: int, db: Session = Depends(database.get_db)):
    """
    API Endpoint: Check the status/progress of a specific bulk request.
    """
    db_request = db.query(models.BulkRequest).filter(models.BulkRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Bulk request not found")
    return db_request


@app.get("/api/certificates/{recipient_id}/download")
def download_certificate(recipient_id: int, db: Session = Depends(database.get_db)):
    """
    API Endpoint: Download the generated PDF certificate for a recipient.
    """
    recipient = db.query(models.Recipient).filter(models.Recipient.id == recipient_id).first()
    
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
        
    if recipient.status != models.StatusEnum.COMPLETED or not recipient.file_path:
        raise HTTPException(status_code=400, detail="Certificate is not ready or failed to generate")
        
    if not os.path.exists(recipient.file_path):
        raise HTTPException(status_code=404, detail="Certificate file not found on server")
        
    # FileResponse automatically handles sending the file to the user's browser
    return FileResponse(
        path=recipient.file_path, 
        filename=os.path.basename(recipient.file_path),
        media_type='application/pdf'
    )
