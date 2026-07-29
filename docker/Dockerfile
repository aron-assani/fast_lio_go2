FROM ros:humble-ros-base

# Install apt packages
RUN apt-get update && apt-get install -y \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-rosidl-default-generators \
    ros-humble-rosidl-generator-dds-idl \
    ros-humble-sensor-msgs \
    ros-humble-nav-msgs \
    ros-humble-pcl-ros \
    ros-humble-pcl-conversions \
    ros-humble-visualization-msgs \
    ros-humble-tf2-ros \
    ros-humble-tf2-eigen \
    ros-humble-tf2-geometry-msgs \
    ros-humble-rviz2 \
    ros-humble-rviz-default-plugins \
    libgl1 \
    libglx-mesa0 \
    nano \
    git \
    build-essential \
    cmake \
    libeigen3-dev \
    libpcl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install livox sdk2 to prevent dependency issues
RUN cd /tmp && \
    git clone https://github.com/Livox-SDK/Livox-SDK2.git && \
    cd Livox-SDK2 && \
    mkdir build && cd build && \
    cmake .. && make -j$(nproc) && make install && \
    rm -rf /tmp/Livox-SDK2

# Clone repos
WORKDIR /root/workspace
RUN mkdir -p src && \
    cd src && \
    git clone --recursive https://github.com/Ericsii/FAST_LIO.git && \
    git clone https://github.com/unitreerobotics/unitree_ros2.git && \
    git clone https://github.com/Livox-SDK/livox_ros_driver2.git

# Build the workspace + configure the livox driver with it's own build script
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    cd src/livox_ros_driver2 && \
    ./build.sh humble"

# Generate the XML
ARG NETWORK_INTERFACE
RUN cat <<EOF > /cyclonedds.xml
<?xml version="1.0" encoding="UTF-8" ?>
<CycloneDDS>
  <Domain>
    <General>
      <Interfaces>
        <NetworkInterface name="${NETWORK_INTERFACE}" priority="default" multicast="default" />
      </Interfaces>
    </General>
  </Domain>
</CycloneDDS>
EOF

# Apply environment variables
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ENV CYCLONEDDS_URI=file:///cyclonedds.xml

# Source environments on terminal entry
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "source /root/workspace/install/setup.bash" >> /root/.bashrc

CMD ["bash"]