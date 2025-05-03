FROM python3.13.1-slim
LABEL authors="stanislavmisko"

ENTRYPOINT ["top", "-b"]