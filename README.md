# rover_sim

URDF model of a small differential-drive rover for ROS 2 Jazzy: two driven
wheels (65 mm, 221.6 mm track) and a rear swivel caster, with a two-deck 3D
printed chassis and a battery bay.

- `urdf/rover.urdf.xacro`: the model. Every dimension and mass is a xacro
  property at the top of the file.
- `meshes/`: STL meshes of the printed parts, used for visuals only.
  Collisions use simple boxes, cylinders and spheres. In Gazebo the wheels
  collide as spheres, so turning matches the wheel odometry.
- `launch/display.launch.py`: robot_state_publisher, joint_state_publisher_gui
  and RViz.
- `launch/gazebo.launch.py`: the rover in Gazebo (Harmonic), driven by
  ros2_control's `diff_drive_controller`.
- `config/controllers.yaml`: controller settings (wheel size, speed limits).
- `worlds/room.sdf`: a small 4 x 3 m room with a few obstacles.

Frames: `base_footprint` (floor) -> `base_link` (on the drive axle) ->
`left_wheel_link`, `right_wheel_link`, `caster_link`, plus empty
`lidar_link` and `camera_link` frames for future sensors.

The caster is modelled as a fixed sphere. Masses of the motors, electronics,
battery and caster, and the sensor positions, are estimates for now.

## Build

```sh
cd ~/ros2_ws
colcon build --packages-select rover_sim
source install/setup.bash
```

## View in RViz

```sh
ros2 launch rover_sim display.launch.py
```

Use the joint_state_publisher_gui sliders to spin the wheels.

To check the model without RViz:

```sh
xacro src/rover_sim/urdf/rover.urdf.xacro > /tmp/rover.urdf
check_urdf /tmp/rover.urdf
```

## Drive it in Gazebo

```sh
ros2 launch rover_sim gazebo.launch.py          # add rviz:=true to also open RViz
```

In a second terminal:

```sh
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
  -p stamped:=true -r cmd_vel:=/diff_drive_controller/cmd_vel
```

Keep the teleop terminal focused: `i` forward, `,` back, `j`/`l` turn,
`k` stop. Top speed is limited to 0.3 m/s. Odometry is published on
`/diff_drive_controller/odom` and as the `odom -> base_footprint` transform.

Launch arguments: `world:=<file.sdf>`, `gui:=false` (headless),
`x:=`, `y:=`, `yaw:=` (spawn pose).

## License

MIT, see [LICENSE](LICENSE).
