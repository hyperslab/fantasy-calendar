FROM node:18-alpine

WORKDIR /app/fantasycalendar

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

RUN yarn run build

FROM python:3.11

# so django will use the right settings
ENV CONTAINER=yes

# install msodbc
RUN curl -sSL -O https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN rm packages-microsoft-prod.deb
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# missing static files will blow everything up without this
RUN python manage.py collectstatic --no-input

# non-Azure containers will create a new DB every time that needs to be set up
# this will keep the Azure DB up to date as well
RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
