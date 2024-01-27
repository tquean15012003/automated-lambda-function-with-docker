# Step 1: Pull the base image
FROM public.ecr.aws/lambda/python:3.10

# Step 2: Copy requirements.txt
COPY ./requirements.txt ${LAMBDA_TASK_ROOT}

# Step 3: Install the specified packages
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_md
RUN python -m spacy download zh_core_web_md

# Step 4: Copy function code
COPY ./src ${LAMBDA_TASK_ROOT}

# Step 5: Set the CMD to your handler
CMD [ "main.handler" ]