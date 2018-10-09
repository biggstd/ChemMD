# Declare the base image from which to start from.
FROM python:3.6-stretch

# Install nodejs (see: https://askubuntu.com/a/720814)
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash \
    && apt-get install nodejs \
    && apt-get -yq autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip, a tool for installing Python packages.
RUN pip install --upgrade pip \
    && pip install --pre -i https://pypi.anaconda.org/bokeh/channel/dev/simple\
    --extra-index-url https://pypi.python.org/simple/\
    bokeh\
    pandas\
    isatools\
    && rm -rf ~/.cache/pip

# Copy the contents of ChemMD to the Docker image, then
# install the ChemMD package with the `setup.py` script.
RUN mkdir /opt/ChemMD
COPY . /opt/ChemMD/
WORKDIR /opt/ChemMD/
RUN pip install -r requirements.txt
RUN python setup.py install

# Change the permissions of the bash files in the scripts folder.
RUN chmod +x /opt/ChemMD/scripts/*.sh

# Setup bokeh environment variables. This should be used if access to the
# CDN server for bokeh resources does not work.
# ENV BOKEH_RESOURCES=inline

# Copy the configuration folder.
COPY ./md_config/ /md_config/

# Setup isadream data environment variable.
# See the `config.json` file in the `md_config` directory
# for the declaration of these options.
ENV CHEMMD_CONFIG_PATH="/md_config/config.json"
#ENV CHEMMD_CONFIG=DEFAULT

# Copy the Bokeh applications to the container.
COPY ./bokeh_applications/scatter /opt/bkapps/scatter
COPY ./bokeh_applications/table /opt/bkapps/table
# Copy the test applications to the container.
# TODO: Consider a better way to handle this. Perhaps without changes
#       to the docker file.
COPY tests /tests/

# Declare the entrypoint. This is the script that will be run
# by default when the Docker container launches.
ENTRYPOINT ["/opt/ChemMD/scripts/entrypoint.sh"]