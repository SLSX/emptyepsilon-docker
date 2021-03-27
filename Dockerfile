FROM debian:10 as build
# https://github.com/daid/EmptyEpsilon/wiki/Build-from-sources

ENV VERSION_MAJOR "2020"
ENV VERSION_MINOR "11"
ENV VERSION_PATCH "23"

RUN apt-get update
RUN apt-get install -yqq git build-essential libx11-dev cmake \
  libxrandr-dev mesa-common-dev libglu1-mesa-dev \
  libudev-dev libglew-dev libjpeg-dev libfreetype6-dev \
  libopenal-dev libsndfile1-dev libxcb1-dev \
  libxcb-image0-dev libsfml-dev \
  python3

RUN git clone https://github.com/daid/SeriousProton.git
WORKDIR /SeriousProton
RUN git checkout EE-$VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH
WORKDIR /
RUN git clone https://github.com/daid/EmptyEpsilon.git
WORKDIR /EmptyEpsilon
RUN git checkout EE-$VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH

RUN mkdir -p /EmptyEpsilon/_build
WORKDIR /EmptyEpsilon/_build/
RUN cmake -DCPACK_PACKAGE_VERSION_MAJOR=$VERSION_MAJOR -DCPACK_PACKAGE_VERSION_MINOR=$VERSION_MINOR -DCPACK_PACKAGE_VERSION_PATCH=$VERSION_PATCH  .. -DSERIOUS_PROTON_DIR=../../SeriousProton
RUN make
RUN make install

# use clean image to not take build sources to final image
FROM debian:10

COPY --from=build /usr/local/bin/EmptyEpsilon /usr/local/bin/
COPY --from=build /usr/local/share/emptyepsilon/ /usr/local/share/emptyepsilon/

# libsfml-dev conveniently install most runtime requirements
RUN apt-get update
RUN apt-get install -yqq libsfml-dev libglu1-mesa python3-pip wget

RUN mkdir /epsibot
WORKDIR /epsibot
RUN pip3 install discord.py requests
RUN wget https://cloud.kvaris.de/nextcloud/index.php/s/PenRbyZKt2scnwc/download -o epsibot.py
RUN wget https://cloud.kvaris.de/nextcloud/index.php/s/Zb4GP9qzD2Y3dYw/download -o emptyempsilon.py

RUN echo "default-server = unix:/run/user/1000/pulse/native \n autospawn = no \n daemon-binary = /bin/true \n enable-shm = false" > /etc/pulse/client.conf

RUN useradd -u 1000 -G audio ee
USER ee

ENV DISPLAY :0

RUN /usr/local/bin/EmptyEpsilon headless=scenario_00_basic.lua
# ENTRYPOINT ["/usr/local/bin/EmptyEpsilon"]
# CMD ["fullscreen=0"]
