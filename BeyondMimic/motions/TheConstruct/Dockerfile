FROM osrf/ros:humble-desktop-full

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV COLCON_WS=/colcon_ws

# Install legged_control2
RUN echo "deb [trusted=yes] https://github.com/qiayuanl/legged_buildfarm/raw/jammy-humble-amd64/ ./" | sudo tee /etc/apt/sources.list.d/qiayuanl_legged_buildfarm.list && \
    echo "yaml https://github.com/qiayuanl/legged_buildfarm/raw/jammy-humble-amd64/local.yaml humble" | sudo tee /etc/ros/rosdep/sources.list.d/1-qiayuanl_legged_buildfarm.list && \
    apt-get update && apt-get install -y \
    ros-humble-legged-control-base && \
    echo "deb [trusted=yes] https://github.com/qiayuanl/simulation_buildfarm/raw/jammy-humble-amd64/ ./" | sudo tee /etc/apt/sources.list.d/qiayuanl_simulation_buildfarm.list && \
    echo "yaml https://github.com/qiayuanl/simulation_buildfarm/raw/jammy-humble-amd64/local.yaml humble" | sudo tee /etc/ros/rosdep/sources.list.d/1-qiayuanl_simulation_buildfarm.list && \
    apt-get update && apt-get install -y \
    ros-humble-mujoco-ros2-control

# Install additional ROS 2 packages
RUN echo "deb [trusted=yes] https://github.com/qiayuanl/unitree_buildfarm/raw/jammy-humble-amd64/ ./" | sudo tee /etc/apt/sources.list.d/qiayuanl_unitree_buildfarm.list && \
    echo "yaml https://github.com/qiayuanl/unitree_buildfarm/raw/jammy-humble-amd64/local.yaml humble" | sudo tee /etc/ros/rosdep/sources.list.d/1-qiayuanl_unitree_buildfarm.list && \
    apt-get update && apt-get install -y \
    ros-humble-unitree-description \
    ros-humble-unitree-systems \
    ros-humble-rosbag2-storage-mcap \
    ros-humble-realsense2-description \
    pip
    # && rm -rf /var/lib/apt/lists/*

RUN pip install wandb

# Create colcon workspace
RUN mkdir -p ${COLCON_WS}/src
WORKDIR ${COLCON_WS}

# Clone custom ROS 2 packages
RUN cd ${COLCON_WS}/src && \
    git clone https://github.com/HybridRobotics/motion_tracking_controller.git && \
    cd ${COLCON_WS}/src && \
    git clone https://github.com/qiayuanl/unitree_bringup.git

# Initialize rosdep if not already initialized and install dependencies
RUN cd ${COLCON_WS} && \
    rosdep update && \
    echo "===== Checking what rosdep will install =====" && \
    rosdep install --from-paths src --ignore-src -r -y --simulate && \
    echo "===== Actually installing dependencies =====" && \
    rosdep install --from-paths src --ignore-src -r -y

# Build the workspace
RUN bash -c "source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=RelwithDebInfo --packages-up-to unitree_bringup && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=RelwithDebInfo --packages-up-to motion_tracking_controller"

# Setup entrypoint
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Source ROS 2 setup\n\
source /opt/ros/humble/setup.bash\n\
\n\
# Source workspace setup if it exists\n\
if [ -f "/colcon_ws/install/setup.bash" ]; then\n\
    source /colcon_ws/install/setup.bash\n\
fi\n\
\n\
exec "$@"' > /ros_entrypoint.sh && \
    chmod +x /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
