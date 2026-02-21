"""CLI runner for development agents."""

import argparse

from .implementation_agent import ImplementationAgent
from .orchestrator_agent import OrchestratorAgent
from .testing_agent import TestingAgent


def run_orchestrator(cycles: int = 1):
    """
    Run the orchestrator agent.

    Args:
        cycles: Number of implementation cycles to run
    """
    print("=" * 60)
    print("Starting Orchestrator Agent")
    print("=" * 60)

    orchestrator = OrchestratorAgent()

    if cycles == 1:
        # Run single cycle
        result = orchestrator.run()
        print("\n" + "=" * 60)
        print("Cycle Results:")
        print(f"  Status: {result['cycle_result']['status']}")
        print(f"  Phases: {len(result['cycle_result']['phases'])}")
        print(f"  Report saved to: {result['report_path']}")
    else:
        # Run multiple cycles
        results = orchestrator.run_continuous_integration(max_cycles=cycles)
        print("\n" + "=" * 60)
        print(f"Completed {len(results)} cycles")
        for i, result in enumerate(results, 1):
            print(f"  Cycle {i}: {result['status']}")

        # Generate final report
        report = orchestrator.generate_report()
        orchestrator.write_file("dev_report.md", report)
        print("\nFinal report saved to: dev_report.md")

    print("=" * 60)


def run_implementation():
    """Run the implementation agent."""
    print("=" * 60)
    print("Starting Implementation Agent")
    print("=" * 60)

    agent = ImplementationAgent()
    stats = agent.run()

    print("\n" + "=" * 60)
    print("Implementation Agent Results:")
    print(f"  Total tasks: {stats['total']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Failed: {stats['failed']}")
    print("=" * 60)


def run_testing():
    """Run the testing agent."""
    print("=" * 60)
    print("Starting Testing Agent")
    print("=" * 60)

    agent = TestingAgent()
    stats = agent.run()

    print("\n" + "=" * 60)
    print("Testing Agent Results:")
    print(f"  Total tasks: {stats['total']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Failed: {stats['failed']}")
    print("=" * 60)


def main():
    """Main CLI entry point for agents."""
    parser = argparse.ArgumentParser(
        description="Markdown CMS Development Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m markdown_cms.agents.cli orchestrator          # Run single cycle
  python -m markdown_cms.agents.cli orchestrator -c 5     # Run 5 cycles
  python -m markdown_cms.agents.cli implementation        # Run implementation agent
  python -m markdown_cms.agents.cli testing               # Run testing agent
        """,
    )

    parser.add_argument(
        "agent",
        choices=["orchestrator", "implementation", "testing"],
        help="Agent to run",
    )
    parser.add_argument(
        "-c",
        "--cycles",
        type=int,
        default=1,
        help="Number of cycles to run (orchestrator only)",
    )

    args = parser.parse_args()

    if args.agent == "orchestrator":
        run_orchestrator(cycles=args.cycles)
    elif args.agent == "implementation":
        run_implementation()
    elif args.agent == "testing":
        run_testing()


if __name__ == "__main__":
    main()
