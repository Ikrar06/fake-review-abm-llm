# Main entry point for the fake review simulation

from src.engine import SimulationEngine


if __name__ == "__main__":
    try:
        engine = SimulationEngine()
        engine.run()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
