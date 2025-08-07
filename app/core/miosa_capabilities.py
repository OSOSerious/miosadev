"""
MIOSA Capabilities - Complete context for what MIOSA can build
This defines the full range of solutions MIOSA can create for businesses
"""

MIOSA_CAPABILITIES = {
    "overview": """
    MIOSA is a Business OS Agent that builds complete, custom business operating systems through natural conversation.
    Not templates, not generic tools - actual custom software designed for how each specific business works.
    MIOSA can build ANY business operations software, from simple automation to complex enterprise systems.
    """,
    
    "core_solutions": {
        "customer_sales": {
            "name": "Customer & Sales Systems",
            "capabilities": [
                "CRM Systems: Full customer relationship management with pipeline tracking, deal stages, contact management, activity logging",
                "Support Platforms: Ticket routing, priority queuing, SLA tracking, customer portals, knowledge bases",
                "Booking Systems: Calendar integration, availability management, payment processing, reminder automation",
                "Lead Management: Lead scoring, qualification workflows, assignment rules, follow-up automation",
                "Quote & Proposal: Dynamic pricing, template management, e-signatures, version tracking"
            ]
        },
        
        "operations_workflow": {
            "name": "Operations & Workflow",
            "capabilities": [
                "Task Management: Project tracking, assignments, deadlines, dependencies, Gantt charts",
                "Inventory Systems: Stock tracking, reorder points, supplier management, warehouse management",
                "Order Management: Order processing, fulfillment tracking, shipping integration, returns handling",
                "Document Management: Version control, approval workflows, digital signatures, compliance tracking",
                "Process Automation: Workflow builders, conditional logic, trigger systems, batch operations"
            ]
        },
        
        "team_communication": {
            "name": "Team & Communication",
            "capabilities": [
                "Team Workspaces: Shared dashboards, real-time collaboration, file sharing, activity feeds",
                "Internal Tools: Admin panels, configuration systems, employee portals, onboarding systems",
                "Communication Hubs: Unified messaging, announcement systems, feedback loops, surveys",
                "Knowledge Management: Wikis, documentation systems, training modules, resource libraries",
                "Performance Systems: Goal tracking, OKRs, reviews, 1-on-1 management"
            ]
        },
        
        "data_analytics": {
            "name": "Data & Analytics",
            "capabilities": [
                "Business Intelligence: KPI dashboards, trend analysis, predictive metrics, custom reports",
                "Data Pipelines: ETL processes, data warehousing, real-time processing, API integrations",
                "Monitoring Systems: Performance tracking, alert systems, anomaly detection, health checks",
                "Reporting Engines: Scheduled reports, custom queries, export systems, visualization tools",
                "Predictive Analytics: Forecasting, pattern recognition, risk assessment, optimization models"
            ]
        },
        
        "financial_admin": {
            "name": "Financial & Administrative",
            "capabilities": [
                "Invoicing Systems: Quote generation, invoice creation, payment tracking, recurring billing",
                "Expense Management: Receipt capture, approval workflows, reimbursements, budget tracking",
                "Time Tracking: Timesheets, project allocation, billing rates, productivity analytics",
                "Compliance Systems: Audit trails, regulatory reporting, policy management, training tracking",
                "Accounting Integration: QuickBooks sync, tax preparation, financial reporting, reconciliation"
            ]
        },
        
        "marketing_growth": {
            "name": "Marketing & Growth",
            "capabilities": [
                "Email Automation: Campaign management, segmentation, personalization, A/B testing",
                "Content Management: CMS systems, publishing workflows, SEO optimization, asset management",
                "Analytics Platforms: Conversion tracking, attribution modeling, cohort analysis, funnel optimization",
                "Referral Systems: Partner portals, affiliate tracking, reward management, commission calculation",
                "Social Media Tools: Publishing, scheduling, engagement tracking, influencer management"
            ]
        }
    },
    
    "industry_specific": {
        "ecommerce": {
            "name": "E-commerce Solutions",
            "capabilities": [
                "Product catalogs with variants and bundles",
                "Shopping cart and checkout systems",
                "Payment gateway integrations",
                "Shipping calculators and label printing",
                "Inventory sync across channels",
                "Review and rating systems",
                "Abandoned cart recovery",
                "Loyalty programs"
            ]
        },
        
        "saas": {
            "name": "SaaS Platform Features",
            "capabilities": [
                "Subscription management and billing",
                "Usage tracking and metering",
                "Feature flags and gradual rollouts",
                "Multi-tenant architecture",
                "API rate limiting",
                "User onboarding flows",
                "In-app messaging",
                "Churn prediction"
            ]
        },
        
        "marketplace": {
            "name": "Marketplace Systems",
            "capabilities": [
                "Vendor management portals",
                "Commission and payout systems",
                "Dispute resolution workflows",
                "Escrow and payment splitting",
                "Rating and review systems",
                "Search and discovery",
                "Trust and safety tools",
                "Analytics for sellers"
            ]
        },
        
        "agency": {
            "name": "Agency Management",
            "capabilities": [
                "Client portals with project visibility",
                "Proposal and contract management",
                "Time and expense tracking",
                "Resource allocation",
                "Project templates",
                "Client feedback systems",
                "Portfolio showcases",
                "Retainer management"
            ]
        },
        
        "healthcare": {
            "name": "Healthcare Systems",
            "capabilities": [
                "Patient scheduling and reminders",
                "Electronic health records",
                "Prescription management",
                "Insurance verification",
                "Telehealth platforms",
                "HIPAA-compliant messaging",
                "Billing and claims",
                "Provider networks"
            ]
        },
        
        "real_estate": {
            "name": "Real Estate Solutions",
            "capabilities": [
                "Property listings and search",
                "Tenant screening and applications",
                "Lease management",
                "Maintenance request systems",
                "Rent collection",
                "Property inspection tools",
                "Market analysis",
                "Commission tracking"
            ]
        }
    },
    
    "technical_capabilities": {
        "backend": [
            "REST APIs with any endpoint structure",
            "GraphQL APIs",
            "Real-time websocket connections",
            "Database schemas with complex relationships",
            "Authentication & authorization systems",
            "Third-party integrations (Stripe, Twilio, SendGrid, Slack, etc.)",
            "Webhook handlers and event systems",
            "Batch processing and job queues",
            "File upload and storage systems",
            "Export/import functionality",
            "Multi-tenant architectures",
            "Microservices architecture",
            "Serverless functions"
        ],
        
        "frontend": [
            "Responsive web applications",
            "Progressive web apps (PWA)",
            "Real-time dashboards",
            "Data visualization (charts, graphs, maps)",
            "Drag-and-drop interfaces",
            "Mobile-optimized views",
            "Dark/light theme support",
            "Accessibility compliance (WCAG)",
            "Multi-language support",
            "Offline functionality",
            "Custom form builders",
            "Rich text editors",
            "File preview systems"
        ],
        
        "integrations": [
            "Payment: Stripe, PayPal, Square, Plaid",
            "Communication: Twilio, SendGrid, Mailchimp, Slack",
            "Storage: AWS S3, Google Cloud Storage, Dropbox",
            "Analytics: Google Analytics, Mixpanel, Segment",
            "CRM: Salesforce, HubSpot, Pipedrive",
            "Accounting: QuickBooks, Xero, FreshBooks",
            "Calendar: Google Calendar, Outlook, Calendly",
            "Maps: Google Maps, Mapbox",
            "AI/ML: OpenAI, Claude, Custom models"
        ]
    },
    
    "problem_patterns": {
        "email_overload": {
            "indicators": ["emails", "inbox", "messages", "communication", "replies"],
            "solutions": [
                "Email parsing and categorization",
                "Auto-response systems",
                "Task extraction from emails",
                "Priority inbox with smart filters",
                "Team assignment routing",
                "Customer portal to reduce emails",
                "FAQ and knowledge base",
                "Unified communication hub"
            ]
        },
        
        "manual_processes": {
            "indicators": ["manual", "spreadsheet", "copy paste", "repetitive", "time-consuming"],
            "solutions": [
                "Workflow automation",
                "Data entry automation",
                "Document generation",
                "Approval workflows",
                "Integration between systems",
                "Batch processing",
                "Scheduled tasks",
                "API connections"
            ]
        },
        
        "customer_management": {
            "indicators": ["customers", "clients", "support", "service", "satisfaction"],
            "solutions": [
                "CRM implementation",
                "Support ticket system",
                "Customer portal",
                "Self-service options",
                "Feedback systems",
                "Loyalty programs",
                "Communication tracking",
                "Service level management"
            ]
        },
        
        "data_visibility": {
            "indicators": ["reporting", "analytics", "metrics", "dashboard", "insights", "tracking"],
            "solutions": [
                "Real-time dashboards",
                "Custom reports",
                "KPI tracking",
                "Predictive analytics",
                "Data warehousing",
                "Alert systems",
                "Trend analysis",
                "Export capabilities"
            ]
        },
        
        "scaling_issues": {
            "indicators": ["growth", "scaling", "bottleneck", "capacity", "overwhelming"],
            "solutions": [
                "Process standardization",
                "Automation systems",
                "Team collaboration tools",
                "Resource planning",
                "Performance optimization",
                "Load balancing",
                "Queue management",
                "Capacity planning"
            ]
        }
    },
    
    "value_metrics": {
        "time_savings": {
            "manual_data_entry": "5-10 hours/week saved",
            "email_management": "2-3 hours/day saved",
            "report_generation": "4-6 hours/week saved",
            "customer_response": "50-80% faster",
            "decision_making": "Real-time vs. weekly",
            "onboarding": "75% reduction in time",
            "invoice_processing": "90% faster"
        },
        
        "business_impact": {
            "revenue_increase": "15-40% from better pipeline visibility",
            "cost_reduction": "20-30% from automation",
            "customer_satisfaction": "25-35% improvement",
            "team_productivity": "30-50% increase",
            "error_reduction": "70-90% fewer mistakes",
            "sales_cycle": "20-30% shorter",
            "customer_retention": "15-25% improvement"
        },
        
        "operational_metrics": {
            "response_time": "Minutes vs. hours",
            "processing_speed": "10x faster",
            "data_accuracy": "99%+ accuracy",
            "system_uptime": "99.9% availability",
            "scalability": "Handle 100x volume",
            "integration_time": "Days vs. months",
            "roi_timeline": "3-6 month payback"
        }
    },
    
    "consultation_guidance": {
        "discovery_framework": [
            "What manual process is being replaced?",
            "What decisions need to be made faster?",
            "What information is currently hidden?",
            "What could be predicted or prevented?",
            "What would 10x growth require?",
            "What's the cost of not solving this?",
            "What have they tried before?",
            "What's their dream outcome?"
        ],
        
        "solution_principles": [
            "Build custom solutions, not generic tools",
            "Start simple, evolve with the business",
            "Automate the repetitive, augment the strategic",
            "Make complex things simple",
            "Focus on business outcomes, not features",
            "Design for tomorrow's scale",
            "Integrate, don't isolate",
            "Measure impact, not activity"
        ]
    }
}

def get_capabilities_context(problem_type: str = None, industry: str = None) -> str:
    """
    Get relevant capabilities context based on problem type or industry
    """
    context_parts = [MIOSA_CAPABILITIES["overview"]]
    
    # Add problem-specific context
    if problem_type:
        for pattern_key, pattern_data in MIOSA_CAPABILITIES["problem_patterns"].items():
            if any(indicator in problem_type.lower() for indicator in pattern_data["indicators"]):
                context_parts.append(f"For {problem_type} problems, MIOSA can build: {', '.join(pattern_data['solutions'])}")
    
    # Add industry-specific context
    if industry and industry.lower() in MIOSA_CAPABILITIES["industry_specific"]:
        industry_data = MIOSA_CAPABILITIES["industry_specific"][industry.lower()]
        context_parts.append(f"For {industry} businesses, MIOSA specializes in: {', '.join(industry_data['capabilities'])}")
    
    return "\n\n".join(context_parts)

def get_solution_suggestions(extracted_info: dict) -> list:
    """
    Get specific solution suggestions based on extracted business information
    """
    suggestions = []
    
    # Check for problem patterns
    if extracted_info.get("problem_description"):
        problem = extracted_info["problem_description"].lower()
        for pattern_key, pattern_data in MIOSA_CAPABILITIES["problem_patterns"].items():
            if any(indicator in problem for indicator in pattern_data["indicators"]):
                suggestions.extend(pattern_data["solutions"][:3])  # Top 3 solutions
    
    # Add industry-specific suggestions
    if extracted_info.get("business_type"):
        business_type = extracted_info["business_type"].lower()
        if business_type in MIOSA_CAPABILITIES["industry_specific"]:
            suggestions.extend(MIOSA_CAPABILITIES["industry_specific"][business_type]["capabilities"][:2])
    
    return suggestions[:5]  # Return top 5 most relevant suggestions

def calculate_impact_metrics(problem_type: str, business_size: str = "small") -> dict:
    """
    Calculate potential impact metrics based on problem and business size
    """
    base_metrics = MIOSA_CAPABILITIES["value_metrics"]
    
    # Adjust based on business size
    multipliers = {
        "solo": 0.5,
        "small": 1.0,
        "medium": 2.5,
        "large": 5.0,
        "enterprise": 10.0
    }
    
    multiplier = multipliers.get(business_size, 1.0)
    
    # Get relevant metrics for the problem type
    impact = {}
    if "email" in problem_type.lower():
        impact["time_saved"] = f"{int(2 * multiplier)}-{int(3 * multiplier)} hours/day"
        impact["response_time"] = "80% faster"
    elif "customer" in problem_type.lower():
        impact["satisfaction"] = "25-35% improvement"
        impact["retention"] = "15-25% better"
    elif "data" in problem_type.lower() or "report" in problem_type.lower():
        impact["decision_speed"] = "Real-time vs. weekly"
        impact["accuracy"] = "99%+ data accuracy"
    else:
        impact["productivity"] = f"{int(30 * multiplier)}-{int(50 * multiplier)}% increase"
        impact["cost_reduction"] = f"{int(20 * multiplier)}-{int(30 * multiplier)}% savings"
    
    return impact