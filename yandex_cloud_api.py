import boto3
from config import BUCKET_NAME
from botocore.exceptions import (
    NoCredentialsError,
    PartialCredentialsError,
    ClientError,
    BotoCoreError,
)
from logger import logging


def yandex_upload_file_s3(file_path, file_name):
    try:
        # Создаем сессию и клиент для работы с Yandex Object Storage
        session = boto3.session.Session()
        s3 = session.client(
            service_name="s3", endpoint_url="https://storage.yandexcloud.net"
        )

        # Загрузка файла
        s3.upload_file(file_path, BUCKET_NAME, file_name)
        logging.info(f"File '{file_name}' successfully uploaded to Yandex Cloud.")

    except NoCredentialsError:
        logging.error(
            "No credentials provided. Please check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
        )
    except PartialCredentialsError:
        logging.error(
            "Incomplete credentials provided. Please ensure both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set."
        )
    except ClientError as e:
        logging.error(f"Client error occurred: {e}")
    except BotoCoreError as e:
        logging.error(f"An error occurred in Boto3: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
