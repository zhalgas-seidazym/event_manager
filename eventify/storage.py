# eventify/storage.py

from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    bucket_name = 'eventify'

    def url(self, name):
        url = super().url(name)
        url = url.replace('minio', 'localhost')
        return url.replace("https://", "http://")  # 💥 хак, но работает

