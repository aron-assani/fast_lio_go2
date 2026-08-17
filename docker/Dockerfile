FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_WS=/root/workspace

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
    ros-humble-pointcloud-to-laserscan \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-nav2-map-server \
    python3-pip \
    eog \
    libgl1 \
    libglx-mesa0 \
    nano \
    git \
    build-essential \
    cmake \
    libeigen3-dev \
    libpcl-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies for execution.py
RUN pip3 install "numpy>=2.0.0" "scipy>=1.14.0" motioncapture pyyaml

# Install Livox SDK2
RUN cd /tmp && \
    git clone https://github.com/Livox-SDK/Livox-SDK2.git && \
    cd Livox-SDK2 && \
    mkdir build && cd build && \
    cmake .. && make -j$(nproc) && make install && \
    rm -rf /tmp/Livox-SDK2

WORKDIR ${ROS_WS}
RUN mkdir -p src

# Clone all required repositories
RUN cd src && \
    git clone --recursive https://github.com/aron-assani/fast_lio_go2 && \
    git clone https://github.com/LihanChen2004/pcd2pgm.git && \
    git clone https://github.com/Livox-SDK/livox_ros_driver2.git && \
    git clone https://github.com/unitreerobotics/unitree_sdk2_python.git

# Install unitree_sdk2_python from source
RUN /bin/bash -c "cd src/unitree_sdk2_python && pip3 install ."

# Build Livox driver separately
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    cd src/livox_ros_driver2 && \
    ./build.sh humble"

# Build the rest of the ROS 2 workspace (fast_lio_go2 and pcd2pgm)
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    colcon build --packages-skip livox_ros_driver2"

# CycloneDDS configuration
ARG NETWORK_INTERFACE=enx2887ba59bf0a
RUN cat <<EOF > ${ROS_WS}/cyclonedds.xml
<?xml version="1.0" encoding="UTF-8" ?>
<CycloneDDS xmlns="https://cdds.io/config" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://cdds.io/config https://raw.githubusercontent.com/eclipse-cyclonedds/cyclonedds/master/etc/cyclonedds.xsd">
    <Domain id="any">
        <General>
            <Interfaces>
                <NetworkInterface name="${NETWORK_INTERFACE}"/>
            </Interfaces>
            <AllowMulticast>true</AllowMulticast>
            <MaxMessageSize>65500B</MaxMessageSize>
        </General>
    </Domain>
</CycloneDDS>
EOF

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ENV CYCLONEDDS_URI=file://${ROS_WS}/cyclonedds.xml

# Environment setup
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc && \
    echo "source ${ROS_WS}/install/setup.bash" >> ~/.bashrc

CMD ["/bin/bash"]