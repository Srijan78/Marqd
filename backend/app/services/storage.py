"""
Cloud Storage Service — Handles file uploads to Google Cloud Storage.

In development mode (no GCS credentials), files are stored locally in the uploads folder.
In production, files are uploaded to the configured GCS bucket.
"""
import os
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class StorageService:
    """Handles file storage — GCS in production, local filesystem in development."""

    @staticmethod
    def upload_file(local_path: str, destination_name: str, content_type: str = None) -> str:
        """
        Upload a file to storage and return the public URL.

        Args:
            local_path: Path to the local file
            destination_name: Target filename in storage (e.g., 'assets/original/uuid.jpg')
            content_type: MIME type of the file

        Returns:
            Public URL of the uploaded file
        """
        env = current_app.config.get("FLASK_ENV", "development")
        bucket_name = current_app.config.get("GCS_BUCKET_NAME")

        if env == "production":
            if not bucket_name:
                raise RuntimeError("GCS_BUCKET_NAME must be configured in production")
            return StorageService._upload_to_gcs(local_path, destination_name, content_type)

        return StorageService._store_locally(local_path, destination_name)

    @staticmethod
    def _upload_to_gcs(local_path: str, destination_name: str, content_type: str = None) -> str:
        """Upload file to Google Cloud Storage."""
        try:
            from google.cloud import storage

            bucket_name = current_app.config["GCS_BUCKET_NAME"]
            project_id = current_app.config.get("GOOGLE_CLOUD_PROJECT")

            # On Cloud Run, ADC is automatically available from the service account.
            client = storage.Client(project=project_id) if project_id else storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(destination_name)

            if content_type:
                blob.content_type = content_type

            blob.upload_from_filename(local_path)

            # Some buckets enforce uniform bucket-level access, where make_public is not allowed.
            # Upload already succeeded, so keep going and rely on bucket IAM/public policy.
            try:
                blob.make_public()
            except Exception as public_exc:
                logger.warning(f"Uploaded to GCS but could not set object ACL public: {public_exc}")

            url = blob.public_url
            logger.info(f"Uploaded to GCS: {url}")
            return url

        except Exception as e:
            logger.error(f"GCS upload failed: {e}", exc_info=True)
            raise RuntimeError("GCS upload failed in production") from e

    @staticmethod
    def _store_locally(local_path: str, destination_name: str) -> str:
        """Store file locally when GCS is not available (development mode)."""
        import shutil

        upload_dir = current_app.config["UPLOAD_FOLDER"]
        # Create subdirectories if needed
        dest_path = os.path.join(upload_dir, destination_name)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        shutil.copy2(local_path, dest_path)
        logger.info(f"Stored locally: {dest_path}")

        # Return a URL-like path for local dev
        return f"/uploads/{destination_name}"

    @staticmethod
    def get_upload_url(destination_name: str) -> str:
        """Get the full URL for an uploaded file."""
        env = current_app.config.get("FLASK_ENV", "development")
        bucket_name = current_app.config.get("GCS_BUCKET_NAME")

        if env == "production" and bucket_name:
            return f"https://storage.googleapis.com/{bucket_name}/{destination_name}"
        else:
            return f"/uploads/{destination_name}"

    @staticmethod
    def delete_file(destination_name: str) -> bool:
        """Delete a file from storage."""
        try:
            env = current_app.config.get("FLASK_ENV", "development")
            bucket_name = current_app.config.get("GCS_BUCKET_NAME")

            if env == "production" and bucket_name:
                from google.cloud import storage
                client = storage.Client()
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(destination_name)
                blob.delete()
            else:
                upload_dir = current_app.config["UPLOAD_FOLDER"]
                dest_path = os.path.join(upload_dir, destination_name)
                if os.path.exists(dest_path):
                    os.remove(dest_path)

            logger.info(f"Deleted: {destination_name}")
            return True

        except Exception as e:
            logger.error(f"Delete failed for {destination_name}: {e}")
            return False
