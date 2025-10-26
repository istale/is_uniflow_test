# Product Context

## Why This Project Exists
The Uniflow Calculation System addresses the need for a modular, extensible approach to arithmetic operations in software systems. Instead of monolithic calculation modules, this system provides separate, well-defined components that can be composed together to create complex calculation workflows.

## Problems It Solves
- Complex arithmetic operations that require multiple steps
- Need for extensible calculation systems that can add new operations easily
- Consistent interfaces for different types of mathematical operations
- Pipeline-based execution of calculation workflows

## How It Should Work
The system follows a registry pattern where different arithmetic operations (addition, multiplication, division) are registered and can be invoked through a common interface. The pipeline system orchestrates these operations to perform complex calculations.

## User Experience Goals
- Clear separation of concerns between different operation types
- Easy extension with new arithmetic operations
- Consistent API across all operation modules
- Reliable pipeline execution for multi-step calculations
