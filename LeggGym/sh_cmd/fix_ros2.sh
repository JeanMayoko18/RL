#!/bin/bash
echo "🧹 Nettoyage de ROS 2 partiel ou cassé..."
sudo apt purge '^ros-humble-*' -y
sudo apt autoremove -y
sudo apt clean

echo "📦 Ajout des sources ROS 2 officielles (si manquantes)..."
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

echo "📦 Installation de ROS 2 Humble Desktop complet..."
sudo apt update
sudo apt install ros-humble-desktop -y

echo "📦 Installation des paquets Gazebo et ROS 2 complémentaires..."
sudo apt install -y \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros-control \
  ros-humble-turtlebot3-gazebo \
  ros-humble-launch \
  ros-humble-launch-ros \
  ros-humble-launch-yaml \
  ros-humble-launch-xml

echo "🧼 Nettoyage de ~/.zshrc des lignes invalides..."
sed -i '/gazebo\\/setup.sh/d' ~/.zshrc
sed -i '/ros2_ws\\/setup.sh/d' ~/.zshrc
sed -i '/local_setup.sh/d' ~/.zshrc

echo "✅ Terminé. Tu peux maintenant tester ROS 2 :"
echo "1️⃣ Ouvre un nouveau terminal"
echo "2️⃣ Tape : source /opt/ros/humble/setup.bash"
echo "3️⃣ Puis : ros2 launch demo_nodes_cpp talker_listener.launch.py"