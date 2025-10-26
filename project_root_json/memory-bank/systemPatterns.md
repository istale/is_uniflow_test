# System Patterns

## System Architecture
The Uniflow Calculation System follows a modular architecture with clear separation of concerns. The system is composed of several distinct modules that work together through well-defined interfaces.

## Key Technical Decisions
- **Registry Pattern**: Operations are registered in a central registry for easy discovery and invocation
- **Pipeline Architecture**: Complex calculations are orchestrated through a pipeline execution system
- **Modular Design**: Each arithmetic operation (addition, multiplication, division) is implemented in its own module
- **Consistent API**: All operation modules follow the same interface pattern

## Design Patterns in Use
- **Registry Pattern**: The a01_registry module serves as the central registry for all arithmetic operations
- **Pipeline Pattern**: The c01_invoker module orchestrates the execution of calculation pipelines
- **Strategy Pattern**: Different arithmetic operations can be selected and executed based on requirements
- **Module Pattern**: Each operation type is encapsulated in its own module for clear separation

## Component Relationships
1. **Registry** (a01_registry) - Central hub for operation registration
2. **Operations** (b02_addition, b03_multiply, b04_divide) - Individual arithmetic implementations
3. **Invoker** (c01_invoker) - Pipeline orchestrator
4. **Calculation** (c02_calculation, c03_more_calculation) - Core calculation logic

## Critical Implementation Paths
- Registry initialization and operation registration
- Pipeline execution flow from invoker to individual operations
- Error handling in calculation modules
- Extension points for adding new operation types
