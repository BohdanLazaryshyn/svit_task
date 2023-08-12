import os
import patoolib

from datetime import datetime

from config import db, app, ALLOWED_EXTENSIONS
from models import Log


def allowed_file(filename: str):
    """
    Check if the file extension is allowed.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def prepare_file(file_name: str):
    """
    Prepare the file name and path.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file_name}"

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    return filename, file_path


def read_and_save_log_in_db(file_path: str):
    """
    Read the file and save the content in the database.
    """
    with app.app_context():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        log = Log(
            content=content,
            file_path=file_path
        )
        db.session.add(log)
        db.session.commit()


def unpack_archive(filename: str, file_path: str):
    """
    Unpack the archive. Save and return the extracted files.
    """
    archive_name = os.path.splitext(filename)[0]
    extracted_folder_path = os.path.join(app.config["UPLOAD_FOLDER"], archive_name)

    os.makedirs(extracted_folder_path, exist_ok=True)
    patoolib.extract_archive(file_path, outdir=extracted_folder_path)

    extracted_files = os.listdir(extracted_folder_path)

    return extracted_files, extracted_folder_path


def time_validations(start_date: str = None, end_date: str = None):
    """
    Validate the start and end date for a correct search of files.
    """
    if start_date and end_date:
        if start_date > end_date:
            return None, None, "Start date must be before End date."
    if start_date:
        start_date_str = start_date.replace("T", " ")
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M")
        if start_date > datetime.now():
            return None, None, "Start date must be before now."
    if end_date:
        end_date_str = end_date.replace("T", " ")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M")
        if end_date > datetime.now():
            return None, None, "End date must be before now."
    return start_date, end_date, None


def filter_logs(
        start_date: str,
        end_date: str,
        keyword: str,
        order: str
):
    """
    Filter the logs based on the parameters.
    """
    query = db.session.query(Log)
    if start_date:
        query = query.filter(Log.date >= start_date)

    if end_date:
        query = query.filter(Log.date <= end_date)

    if keyword:
        query = query.filter(Log.content.contains(keyword))

    if order == "newest":
        query = query.order_by(Log.date.desc())
    elif order == "oldest":
        query = query.order_by(Log.date)

    return query
