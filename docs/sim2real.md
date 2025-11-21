---
title: Full SIM2REAL Pipeline
layout: page
---

# SIM2REAL — Full Detailed Guide

## Complete Deployment Workflow

```mermaid
flowchart TD
    A[Sim Policy (ONNX/PT)] --> B[Unitree SDK Node]
    B --> C[ROS2 Control Stack]
    C --> D[Real-time (500Hz) Control Loop]
    D --> E[Unitree G1]
```

## Critical Components

### 1. Joint Mapping
Simulation → hardware:
- offsets
- sequence
- scaling
- torque limits

### 2. Low-Level Control
Three possible modes:
- torque control
- position control
- hybrid impedance

### 3. Domain Adaptation
Add during simulation:
- latency (2–8 ms)
- IMU noise
- foot contact noise
- link mass scaling

### 4. Safety
- joint limit clamping
- fall detection
- emergency stop
- watchdog timers

### 5. Deployment Procedure
1. Stand test  
2. CoM tuning  
3. Slow walk  
4. Dynamic gait  
5. Complex whole-body moves  
