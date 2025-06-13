FROM python:3.12.5-slim-bookworm

# Upgrade -- let's avoid this to reduce the size of the image
# RUN apt-get update && apt-get -y upgrade

# Create a non-root user.
RUN useradd -m -u 1000 app_user

# Switch to the non-root user
ENV HOME="/home/app_user"
USER app_user
# Set the working directory in the container
WORKDIR ${HOME}/app

RUN pip install --upgrade pip
RUN pip install frankfurtermcp

# Copy the wheel file to the container without caring about the version
# MAKE SURE TO BUILD THE WHEEL FIRST AND MAKE SURE THAT THERE IS ONLY ONE WHEEL FILE IN THE dist FOLDER
# COPY ./dist/frankfurtermcp-*.whl ./dist/
# RUN pip install --upgrade pip wheel ./dist/frankfurtermcp-*.whl

# Run the application
ENTRYPOINT ["sh", "-c"]
CMD ["PORT=${PORT} FASTMCP_PORT=${PORT} python -m frankfurtermcp.server"]
EXPOSE ${FASTMCP_PORT}
