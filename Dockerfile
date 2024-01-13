FROM public.ecr.aws/lambda/python:3.10

# Copy requirements.txt
COPY ./requirements.txt ${LAMBDA_TASK_ROOT}

# Copy function code
COPY ./src ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handler" ]