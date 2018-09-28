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
RUN python setup.py install

# Setup bokeh environment variables.
ENV BOKEH_RESOURCES=inline

# Setup isadream data environment variable.
# See the `config.json` file in the `md_config` directory
# for the declaration of these options.
ENV DREAM_CONFIG=DEFAULT

# TODO: Set up the directories for each Bokeh application.
#COPY ./bokehtest /bokehtest
#COPY ./NMRDemo /NMRDemo
#COPY ./testvis /testvis

# Add entrypoint (this allows variable expansion).
# TODO: Add Bokeh application directories to entrypoint.sh.
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Declare the entrypoint. This is the script that will be run
# by default when the Docker container launches.
ENTRYPOINT ["/entrypoint.sh"]