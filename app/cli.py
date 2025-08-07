"""
MIOSA CLI - Interactive AI Application Builder
"""

import asyncio
import sys
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.styles import Style
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
except ImportError:
    print("Missing required packages. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "prompt-toolkit", "rich", "nest-asyncio"])
    from prompt_toolkit import prompt
    from prompt_toolkit.styles import Style
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table

from app.orchestration.coordinator import ApplicationGenerationCoordinator

console = Console()

class MiosaCLI:
    def __init__(self):
        self.coordinator = ApplicationGenerationCoordinator()
        self.session_id = None
        self.current_phase = "initial"
        self.style = Style.from_dict({
            '': '#00aa00 bold',
        })
        # Token tracking
        self.metrics = {
            "calls": 0,
            "tokens": 0,
            "cost": 0.0
        }
        
    async def start(self):
        """Start the CLI chat interface"""
        self._show_welcome()
        
        # Start onboarding-first prompt
        console.print("\n[bold cyan]I'm MIOSA. First, what's your name?[/bold cyan]\n")
        
        # Main chat loop
        while True:
            try:
                # Get user input
                user_input = prompt("\n💬 You: ", style=self.style)
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    self._show_goodbye()
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'status':
                    self._show_status()
                    continue
                
                if user_input.lower() == 'metrics':
                    self._show_metrics()
                    continue
                
                # Map build intent phrases to 'generate'
                normalized = user_input.strip().lower()
                build_aliases = [
                    'start now', 'begin', 'build it', "let's go", 'lets go', 'do it',
                    'start building', 'get started', "let's begin", 'build this', 'create this', 'implement'
                ]
                if normalized == 'generate' or any(alias == normalized for alias in build_aliases):
                    # Check if session is ready for generation
                    if self.session_id:
                        session = self.coordinator.get_session(self.session_id)
                        if session and session.get('ready_for_generation'):
                            await self._generate_application()
                        else:
                            console.print("[red]Not ready to generate yet. Please complete the consultation first.[/red]")
                    else:
                        console.print("[red]No active session. Start by describing your application.[/red]")
                    continue
                
                # Process consultation message
                await self._process_message(user_input)
                    
            except KeyboardInterrupt:
                console.print("\n")
                self._show_goodbye()
                break
            except Exception as e:
                console.print(f"\n[red]❌ Error: {e}[/red]")
                console.print("[dim]Type 'help' for assistance[/dim]")
    
    async def _process_message(self, message: str):
        """Process user message through consultation"""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task(description="Thinking...", total=None)
            
            try:
                if not self.session_id:
                    # Start new consultation
                    self.session_id = str(uuid.uuid4())
                    result = await self.coordinator.start_consultation(
                        self.session_id, 
                        message
                    )
                else:
                    # Continue consultation - onboarding-aware
                    result = await self.coordinator.continue_consultation(
                        self.session_id,
                        message
                    )
                
                # Update phase from result
                self.current_phase = result.get("phase", self.current_phase)
                
                # Update metrics (mock for now - in real implementation, get from LLM service)
                self.metrics["calls"] += 1
                self.metrics["tokens"] += len(message.split()) * 10  # Rough estimate
                self.metrics["cost"] += 0.001  # Rough estimate
                
            except Exception as e:
                console.print(f"[red]Error processing message: {e}[/red]")
                return
        
        # Display personalized response
        user_profile = result.get('user_profile', {})
        user_name = user_profile.get('name', '')
        
        # Show personalized header for responses
        if user_name and result.get('onboarding_complete'):
            business_name = user_profile.get('business_name', '')
            if business_name:
                console.print(f"\n🤖 [bold cyan]MIOSA for {user_name} ({business_name}):[/bold cyan] {result.get('response', 'I understand. Let me help you with that.')}\n")
            else:
                console.print(f"\n🤖 [bold cyan]MIOSA for {user_name}:[/bold cyan] {result.get('response', 'I understand. Let me help you with that.')}\n")
        else:
            console.print(f"\n🤖 [bold cyan]MIOSA:[/bold cyan] {result.get('response', 'I understand. Let me help you with that.')}\n")
        
        # Show detailed progress
        self._show_detailed_progress(result)
        
        # Show solution if provided
        if result.get('solution'):
            solution = result['solution']
            console.print("\n" + "="*50)
            console.print("[bold green]💡 RECOMMENDED SOLUTION[/bold green]")
            console.print("="*50)
            console.print(f"[cyan]Type:[/cyan] {solution.get('recommended_solution')}")
            console.print(f"[cyan]Stack:[/cyan] {solution.get('technical_stack')}")
            console.print(f"[cyan]Features:[/cyan] {', '.join(solution.get('core_features', []))}")
            console.print(f"[cyan]Impact:[/cyan] {solution.get('estimated_impact')}")
            console.print("="*50 + "\n")
        
        # Progress is now handled in _show_detailed_progress
        
        # Check if ready to generate
        if result.get('ready_for_generation'):
            console.print("\n[bold green]✅ Consultation complete![/bold green]")
            console.print("[yellow]Type 'generate' to build your application, or continue refining requirements.[/yellow]")
    
    async def _generate_application(self):
        """Generate the complete application"""
        console.print("\n" + "="*60)
        console.print("[bold cyan]🏗️  GENERATING YOUR APPLICATION[/bold cyan]")
        console.print("="*60 + "\n")
        
        with Progress(console=console) as progress:
            task = progress.add_task("[cyan]Generating application...", total=100)
            
            try:
                # Update progress through stages
                stages = [
                    ("Extracting requirements", 10),
                    ("Designing database", 25),
                    ("Generating backend", 50),
                    ("Creating frontend", 75),
                    ("Setting up integrations", 90),
                    ("Finalizing deployment", 100)
                ]
                
                for stage_name, progress_value in stages:
                    progress.update(task, description=f"[cyan]{stage_name}...", completed=progress_value)
                    await asyncio.sleep(0.5)  # Simulate work
                
                # Actually generate the application
                result = await self.coordinator.generate_application(self.session_id)
                
                progress.update(task, completed=100, description="[green]✅ Complete!")
                
            except Exception as e:
                console.print(f"\n[red]❌ Generation failed: {e}[/red]")
                return
        
        # Show results
        self._show_generation_results(result)
    
    def _show_generation_results(self, result: Dict[str, Any]):
        """Display generation results"""
        console.print("\n" + "="*60)
        console.print("[bold green]✨ APPLICATION GENERATED SUCCESSFULLY![/bold green]")
        console.print("="*60 + "\n")
        
        # Project info
        console.print(f"📁 Project ID: [cyan]{result.get('project_id', 'N/A')}[/cyan]")
        console.print(f"📊 Status: [green]{result.get('status', 'N/A')}[/green]\n")
        
        # Components summary
        if 'components' in result:
            table = Table(title="Generated Components", show_header=True, header_style="bold magenta")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Details")
            
            components = result['components']
            
            if 'database' in components:
                db = components['database']
                table.add_row(
                    "Database", 
                    "✅ Generated",
                    f"{len(db.get('tables', []))} tables"
                )
            
            if 'backend' in components:
                backend = components['backend']
                table.add_row(
                    "Backend API",
                    "✅ Generated", 
                    f"{backend.get('framework', 'FastAPI')}"
                )
            
            if 'frontend' in components:
                frontend = components['frontend']
                table.add_row(
                    "Frontend",
                    "✅ Generated",
                    f"{frontend.get('framework', 'React')}"
                )
            
            if 'integrations' in components:
                integrations = components.get('mcp_connectors', [])
                table.add_row(
                    "Integrations",
                    "✅ Configured",
                    f"{len(integrations)} tools"
                )
            
            console.print(table)
        
        # Summary
        if 'summary' in result:
            console.print(f"\n📝 [bold]Summary:[/bold]\n{result['summary']}")
        
        console.print("\n[bold yellow]🎉 Your application is ready![/bold yellow]")
        console.print("[dim]Check the generated files in your project directory.[/dim]\n")
    
    def _show_welcome(self):
        """Display welcome message"""
        console.clear()
        
        # Personalized header based on session/user_profile when available
        header_text = """[bold cyan]🤖 MIOSA - Your Personal Business OS Agent[/bold cyan]
            
I build custom software that runs YOUR business exactly how you want.
No templates. No generic solutions. Just your perfect system.

[yellow]Commands:[/yellow]
• [green]generate[/green] - Start building your application  
• [green]status[/green]   - Show current progress
• [green]metrics[/green]  - Show token usage and costs
• [green]help[/green]     - Show available commands
• [green]exit[/green]     - Exit MIOSA

[bold]Let's start with a quick introduction so I can build something perfect for your needs.[/bold]"""
        panel = Panel.fit(header_text, border_style="cyan", padding=(1, 2))
        console.print(panel)
    
    def _show_goodbye(self):
        """Display goodbye message"""
        console.print("\n[bold cyan]Thanks for using MIOSA! 👋[/bold cyan]")
        console.print("[dim]Your session has been saved.[/dim]\n")
    
    def _show_help(self):
        """Display help information"""
        help_text = """
[bold cyan]MIOSA Help[/bold cyan]

[yellow]How to use:[/yellow]
1. Tell me what's broken in your business
2. I'll ask follow-up questions to understand your needs
3. Type 'generate' when ready to build your solution

[yellow]Commands:[/yellow]
• [green]generate[/green] - Start building (when consultation complete)
• [green]status[/green]   - Show consultation progress  
• [green]metrics[/green]  - Show token usage and costs
• [green]help[/green]     - Show this help
• [green]exit[/green]     - Exit MIOSA

[yellow]What I build:[/yellow]
• Custom CRMs that match how you sell
• Automated workflows that eliminate manual work
• Real-time dashboards that show what matters
• Customer portals that reduce support tickets
• Integration systems that connect your tools

[bold]Just tell me what's slowing down your business![/bold]
"""
        console.print(Panel(help_text, border_style="yellow", title="Help"))
    
    def _show_status(self):
        """Display current consultation status"""
        if not self.session_id:
            console.print("[yellow]No active session. Start by describing your application.[/yellow]")
            return
        
        status_table = Table(title="Consultation Status", show_header=True, header_style="bold cyan")
        status_table.add_column("Property", style="cyan")
        status_table.add_column("Value", style="white")
        
        status_table.add_row("Session ID", self.session_id[:8] + "...")
        status_table.add_row("Current Phase", self.current_phase.title())
        status_table.add_row("Progress", self._get_phase_progress())
        status_table.add_row("Ready to Generate", "✅ Yes" if self.current_phase == "complete" else "❌ Not yet")
        
        console.print(status_table)
        
        # Show quick metrics
        console.print(f"\n[dim]💡 {self.metrics['calls']} calls • {self.metrics['tokens']} tokens • ${self.metrics['cost']:.3f}[/dim]")
    
    def _show_metrics(self):
        """Display token usage metrics"""
        metrics_table = Table(title="Token Usage Metrics", show_header=True, header_style="bold cyan")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="white")
        
        metrics_table.add_row("API Calls", str(self.metrics["calls"]))
        metrics_table.add_row("Tokens Used", f"{self.metrics['tokens']:,}")
        metrics_table.add_row("Estimated Cost", f"${self.metrics['cost']:.4f}")
        
        if self.metrics["calls"] > 0:
            avg_tokens = self.metrics["tokens"] / self.metrics["calls"]
            metrics_table.add_row("Avg Tokens/Call", f"{avg_tokens:.0f}")
        
        console.print(metrics_table)
    
    def _show_detailed_progress(self, result: Dict[str, Any]):
        """Show enhanced progress with details"""
        progress = result.get('progress', 0)
        phase = result.get('phase', 'initial')
        progress_details = result.get('progress_details', {})
        
        # Get user profile for personalization
        user_profile = result.get('user_profile', {})
        user_name = user_profile.get('name', '')
        business_name = user_profile.get('business_name', '')
        
        # Create better progress bar
        bar = self._create_progress_bar(progress)
        
        # Phase description with personalization
        phase_descriptions = {
            'onboarding': f'👋 Getting to know {user_name}' if user_name else '👋 Introduction',
            'consultation': f'🔍 Understanding {business_name}' if business_name else '🔍 Understanding your business',
            'initial': '🚀 Getting started',
            'problem_discovery': '🔍 Understanding your challenge',
            'process_understanding': '⚙️ Learning your workflow',
            'impact_analysis': '📊 Analyzing business impact',
            'requirements_gathering': '📝 Finalizing requirements',
            'building': '🏗️ Building your solution',
            'ready_to_build': '✨ Ready to build!'
        }
        
        phase_desc = phase_descriptions.get(phase, phase.title())
        
        # Show personalized progress
        if user_name and business_name:
            console.print(f"Progress: {bar} {progress}% - {phase_desc}")
        else:
            console.print(f"Progress: {bar} {progress}% - {phase_desc}")
        
        # Show what we know and what we need
        if progress_details:
            known = progress_details.get('known', [])
            needed = progress_details.get('needed', [])
            
            if known:
                console.print(f"[dim]✓ Known: {', '.join(known)}")
            if needed and needed[0] != "Ready to build!":
                console.print(f"[dim]⚠ Need: {', '.join(needed)}")
        
        # Show onboarding step if in onboarding
        onboarding_step = result.get('onboarding_step')
        if onboarding_step and onboarding_step != 'complete':
            step_names = {
                'name': 'Getting your name',
                'email': 'Getting your email',
                'business_name': 'Getting your business name',
                'business_type': 'Understanding your business type',
                'team_size': 'Learning about your team',
                'main_problem': 'Understanding your main challenge'
            }
            step_desc = step_names.get(onboarding_step, onboarding_step)
            console.print(f"[dim]📋 Step: {step_desc}")
        
        console.print()  # Extra line for spacing
    
    def _create_progress_bar(self, percentage: int, width: int = 25) -> str:
        """Create a better looking progress bar"""
        filled = int((percentage / 100) * width)
        empty = width - filled
        
        # Use better characters
        filled_char = '█'
        empty_char = '░'
        
        bar = f"[{filled_char * filled}{empty_char * empty}]"
        return bar
    
    def _show_progress_bar(self, progress_value: Optional[int] = None):
        """Show consultation progress"""
        if progress_value is not None:
            progress = progress_value
        else:
            phases = ["initial", "layer1", "layer2", "layer3", "recommendation"]
            try:
                current_index = phases.index(self.current_phase)
                progress = (current_index + 1) / len(phases) * 100
            except ValueError:
                progress = 0
        
        # Create progress bar
        filled = int(progress / 100 * 30)
        bar = "█" * filled + "░" * (30 - filled)
        
        console.print(f"[dim]Progress:[/dim] {bar} [cyan]{progress:.0f}%[/cyan] - [yellow]{self.current_phase}[/yellow]")
    
    def _get_phase_progress(self):
        """Get current phase progress percentage"""
        phases = {
            "initial": "20%",
            "layer1": "40%",
            "layer2": "60%",
            "layer3": "80%",
            "complete": "100%",
            "recommendation": "100%"
        }
        return phases.get(self.current_phase, "0%")

def run_cli():
    """Run the CLI with proper event loop handling"""
    try:
        # Check if there's already an event loop running
        loop = asyncio.get_running_loop()
        # If we're here, there's already a loop - use nest_asyncio
        cli = MiosaCLI()
        task = loop.create_task(cli.start())
        loop.run_until_complete(task)
    except RuntimeError:
        # No event loop running, create a new one
        cli = MiosaCLI()
        asyncio.run(cli.start())

def main():
    """Main entry point"""
    try:
        run_cli()
    except Exception as e:
        console.print(f"[bold red]Fatal error: {e}[/bold red]")
        console.print("[dim]Please check your configuration and try again.[/dim]")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[cyan]Goodbye! 👋[/cyan]")
        sys.exit(0)