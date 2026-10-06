import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const out = join(__dirname, "..", "app", "data", "questions.json");

const CC = "cloud_concepts";
const AA = "azure_architecture";
const AM = "azure_management";

/** @type {Array<Record<string, unknown>>} */
const questions = [];
let id = 1;

function add(domain, question, options, correct, explanation, study_url, multi = false) {
  questions.push({
    id: id++,
    domain,
    question,
    options,
    correct: Array.isArray(correct) ? correct : [correct],
    explanation,
    study_url,
    multi_select: multi,
  });
}

add(
  CC,
  "Which cloud model gives the consumer the most control over hardware and the operating system?",
  ["Software as a Service (SaaS)", "Platform as a Service (PaaS)", "Infrastructure as a Service (IaaS)", "Function as a Service (FaaS)"],
  2,
  "IaaS provides virtualized compute, storage, and networking while you manage OS, middleware, and apps.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/3-define-cloud-models"
);
add(
  CC,
  "What is a primary benefit of elasticity in cloud computing?",
  ["Fixed monthly cost regardless of usage", "Ability to scale resources up or down based on demand", "Guaranteed physical access to servers", "Elimination of all operational expenditures"],
  1,
  "Elasticity lets workloads consume more or fewer resources as demand changes.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/4-describe-benefits-cloud-services"
);
add(
  CC,
  "CapEx in cloud economics typically refers to:",
  ["Pay-as-you-go operational spending", "Up-front capital spending on physical infrastructure", "Costs of software subscriptions only", "Tax credits for renewable energy"],
  1,
  "Capital expenditure (CapEx) is upfront investment in datacenter assets; cloud shifts much spending to OpEx.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/5-describe-consumption-based-model"
);
add(
  CC,
  "Which deployment model uses resources dedicated to a single organization but may be hosted by a third party?",
  ["Public cloud", "Private cloud", "Hybrid cloud only", "Community cloud only"],
  1,
  "Private cloud is for one organization; it can run on-premises or on dedicated provider infrastructure.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/3-define-cloud-models"
);
add(
  CC,
  "Hybrid cloud is best described as:",
  ["Using only Azure public regions", "Combining public and private cloud with orchestration between them", "Running VMs without networking", "A synonym for multi-cloud"],
  1,
  "Hybrid connects on-premises or private environments with public cloud for flexibility and migration paths.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/3-define-cloud-models"
);
add(
  CC,
  "Which statement about availability zones is TRUE?",
  ["They are the same as Azure regions", "They are physically separate datacenters within a region", "They replace the need for geo-redundancy", "They only exist for SaaS products"],
  1,
  "Availability zones are separate datacenters in a region, designed for high availability within the region.",
  "https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/3-describe-availability-zones"
);
add(
  CC,
  "The shared responsibility model means:",
  ["Microsoft is responsible for all security aspects", "The customer is always responsible for physical datacenter security", "Responsibilities are split between provider and customer depending on the service model", "Developers are not responsible for application code in PaaS"],
  2,
  "Security and management duties depend on IaaS/PaaS/SaaS; the customer always retains data and access responsibilities.",
  "https://learn.microsoft.com/en-us/training/modules/describe-security-privacy-compliance-trust/2-describe-defense-depth"
);
add(
  CC,
  "Which is an example of Software as a Service (SaaS)?",
  ["Azure Virtual Machines", "Azure App Service", "Microsoft 365 online email", "Azure Kubernetes Service"],
  2,
  "Microsoft 365 is consumed as software over the internet with the provider managing the stack.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/3-define-cloud-models"
);
add(
  CC,
  "Geo-redundancy primarily helps with:",
  ["Lower latency in a single city", "Protecting against regional disasters by replicating to another region", "Eliminating the need for backups", "Reducing VM size"],
  1,
  "Pairing regions supports disaster recovery when an entire region is unavailable.",
  "https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/4-describe-regions"
);
add(
  CC,
  "Serverless computing in Azure is most closely associated with:",
  ["Manual patch management of OS disks", "Azure Functions and event-driven execution", "Purchasing physical servers", "Dedicated hosts only"],
  1,
  "Functions abstracts servers; you run code on triggers and pay for execution.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/6-describe-azure-functions"
);
add(
  CC,
  "Which pricing model charges based on actual resource consumption?",
  ["Reserved capacity only", "Consumption-based (pay-as-you-go)", "Perpetual license with no usage metering", "Fixed CapEx lease"],
  1,
  "Consumption-based billing aligns cost with metered usage of services.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/5-describe-consumption-based-model"
);
add(
  CC,
  "A service level agreement (SLA) defines:",
  ["Marketing slogans for Azure", "Committed uptime and connectivity thresholds with potential service credits", "The price list for all third-party SaaS", "Developer coding standards"],
  1,
  "SLAs document expected service performance such as uptime percentages.",
  "https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/6-describe-service-level-agreements"
);
add(
  CC,
  "Which option best describes scalability?",
  ["Ability to handle increased load by adding resources", "Fixed capacity that never changes", "Running only one VM forever", "Manual hardware installation on-premises only"],
  0,
  "Scalability is growing or shrinking capacity to meet demand.",
  "https://learn.microsoft.com/en-us/training/paths/az-900-describe-cloud-concepts/"
);
add(
  CC,
  "Fault tolerance means:",
  ["System continues operating when components fail", "Zero cost for all services", "No need for backups", "Single point of failure is required"],
  0,
  "Fault tolerance designs for component failures without total outage.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/4-describe-benefits-cloud-services"
);
add(
  CC,
  "Which is NOT a characteristic of cloud computing per common definitions?",
  ["On-demand self-service", "Broad network access", "Manual-only provisioning with no automation", "Measured service"],
  2,
  "Cloud emphasizes on-demand provisioning; manual-only provisioning contradicts cloud characteristics.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cloud-compute/2-describe-cloud-computing"
);

add(
  AA,
  "Azure Resource Manager (ARM) templates are used to:",
  ["Monitor CPU only", "Define infrastructure as code for repeatable deployments", "Replace Azure AD", "Encrypt disks automatically without configuration"],
  1,
  "ARM templates declare resources and dependencies for consistent deployments.",
  "https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/7-describe-azure-resource-manager"
);
add(
  AA,
  "Which Azure service provides DNS domain hosting?",
  ["Azure Firewall", "Azure DNS", "Azure Load Balancer", "Azure Bastion"],
  1,
  "Azure DNS hosts DNS domains and records with Azure infrastructure.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/4-describe-azure-dns"
);
add(
  AA,
  "Azure Virtual Network (VNet) is primarily used to:",
  ["Store unstructured blobs", "Provide private network isolation and segmentation in Azure", "Run SQL queries", "Manage RBAC roles"],
  1,
  "VNets isolate workloads and connect to on-premises via VPN or ExpressRoute.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/3-describe-azure-virtual-networks"
);
add(
  AA,
  "Which storage tier is intended for rarely accessed data with lowest storage cost and highest retrieval latency?",
  ["Hot", "Cool", "Archive", "Premium block blobs"],
  2,
  "Archive tier is for long-term retention with hours of rehydration latency.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-storage-services/3-describe-storage-tiers"
);
add(
  AA,
  "Azure Blob Storage is best suited for:",
  ["Relational table data with joins", "Object storage for unstructured data such as images and backups", "In-memory caching only", "Active Directory objects"],
  1,
  "Blob storage stores massive amounts of unstructured object data.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-storage-services/2-describe-azure-blob-storage"
);
add(
  AA,
  "Azure Files provides:",
  ["Managed file shares accessible via SMB/NFS", "GPU compute clusters", "Key signing for TLS", "Serverless HTTP triggers"],
  0,
  "Azure Files offers cloud file shares mounted by VMs or on-premises clients.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-storage-services/4-describe-azure-files"
);
add(
  AA,
  "Which compute option gives you full control of the guest operating system?",
  ["Azure Functions consumption plan", "Azure Virtual Machines", "Azure Logic Apps", "Azure CDN"],
  1,
  "VMs are IaaS: you manage the OS and applications inside the VM.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/2-describe-azure-virtual-machines"
);
add(
  AA,
  "Azure App Service is an example of:",
  ["IaaS", "PaaS for hosting web apps", "SaaS email", "Bare-metal servers"],
  1,
  "App Service hosts web apps without managing underlying servers.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/5-describe-azure-app-service"
);
add(
  AA,
  "Azure Kubernetes Service (AKS) helps you:",
  ["Run containers with managed Kubernetes control plane", "Replace Azure AD", "Store archival tapes", "Create DNS zones only"],
  0,
  "AKS simplifies running Kubernetes by managing the control plane.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/7-describe-azure-kubernetes-service"
);
add(
  AA,
  "Which service distributes incoming traffic across healthy backend instances?",
  ["Azure Load Balancer or Application Gateway", "Azure Key Vault", "Azure Policy", "Azure Advisor"],
  0,
  "Load balancers and application gateways distribute traffic for availability and scale.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/8-describe-azure-load-balancer"
);
add(
  AA,
  "Azure SQL Database is:",
  ["A NoSQL document database", "A managed relational PaaS database service", "A local-only SQL Server installer", "A CDN edge cache"],
  1,
  "Azure SQL Database is managed SQL in the cloud with built-in features.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-database-analytics-services/2-describe-azure-sql-database"
);
add(
  AA,
  "Cosmos DB is designed for:",
  ["Globally distributed, multi-model NoSQL with configurable consistency", "Mainframe COBOL workloads only", "On-premises tape backup", "Single-region SQL reporting only"],
  0,
  "Cosmos DB offers global distribution and multiple APIs with SLAs on latency and availability.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-database-analytics-services/3-describe-azure-cosmos-db"
);
add(
  AA,
  "Azure Synapse Analytics is primarily used for:",
  ["Enterprise data warehousing and analytics at scale", "DNS hosting", "VM scale sets only", "Mobile push notifications"],
  0,
  "Synapse integrates big data and SQL analytics capabilities.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-database-analytics-services/5-describe-azure-synapse-analytics"
);
add(
  AA,
  "ExpressRoute provides:",
  ["Private connectivity from on-premises to Azure over a dedicated circuit", "Free public internet-only access", "Automatic VM patching", "Blob tiering"],
  0,
  "ExpressRoute connects on-premises networks to Microsoft cloud over private connections.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/10-describe-azure-expressroute"
);
add(
  AA,
  "Azure CDN improves:",
  ["Delivery speed of static content by caching at edge locations", "Database indexing", "AD password hashing", "Compliance audits"],
  0,
  "CDN caches content closer to users to reduce latency.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/11-describe-azure-content-delivery-network"
);
add(
  AA,
  "Azure Key Vault is used to:",
  ["Host public websites", "Securely store secrets, keys, and certificates", "Run batch ML training only", "Replace Azure Monitor"],
  1,
  "Key Vault centralizes secrets management with access policies and auditing.",
  "https://learn.microsoft.com/en-us/training/modules/describe-security-privacy-compliance-trust/4-describe-azure-key-vault"
);
add(
  AA,
  "Azure Table Storage provides:",
  ["NoSQL key-value storage for structured non-relational data", "Relational joins with foreign keys", "GPU training clusters", "AD domain controllers"],
  0,
  "Table storage stores flexible datasets with a key/entity model.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-storage-services/5-describe-azure-table-storage"
);
add(
  AA,
  "Azure Queue Storage is commonly used for:",
  ["Decoupling application components with asynchronous message queues", "Hosting WordPress directly without compute", "Replacing Azure AD", "Static website HTTPS only"],
  0,
  "Queues buffer work between producers and consumers.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-storage-services/6-describe-azure-queue-storage"
);
add(
  AA,
  "An Azure region is:",
  ["A set of datacenters deployed within a latency-defined perimeter", "A single rack worldwide", "Same as a resource group", "An AD organizational unit"],
  0,
  "Regions are geographic areas containing multiple datacenters.",
  "https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/4-describe-regions"
);
add(
  AA,
  "Azure DDoS Protection helps mitigate:",
  ["Distributed denial-of-service attacks against public endpoints", "Accidental tag deletion only", "SQL schema drift", "Expired SSL on localhost"],
  0,
  "DDoS Protection provides attack mitigation for network layers.",
  "https://learn.microsoft.com/en-us/training/modules/describe-security-privacy-compliance-trust/3-describe-azure-ddos-protection"
);
add(
  AA,
  "Azure Firewall is a:",
  ["Managed cloud-native network firewall service", "Blob tiering feature", "Identity provider", "DevOps pipeline task only"],
  0,
  "Azure Firewall filters traffic with built-in high availability.",
  "https://learn.microsoft.com/en-us/training/modules/describe-security-privacy-compliance-trust/6-describe-azure-firewall"
);
add(
  AA,
  "Azure Bastion provides:",
  ["Secure RDP/SSH to VMs over TLS without public IPs on VMs", "Cheap archival storage", "Cosmos DB consistency levels", "Management group creation"],
  0,
  "Bastion enables browser-based private admin access to VMs.",
  "https://learn.microsoft.com/en-us/training/modules/describe-azure-compute-networking-services/12-describe-azure-bastion"
);

add(
  AM,
  "Azure Policy is used to:",
  ["Enforce organizational standards and compliance at scale", "Send email alerts only", "Replace Azure Cost Management", "Create VM images manually"],
  0,
  "Policy evaluates resources against rules and can deny or remediate non-compliant configurations.",
  "https://learn.microsoft.com/en-us/training/modules/describe-features-tools-manage-deploy-azure-resources/3-describe-azure-policy"
);
add(
  AM,
  "Which tool provides a browser-based unified console for managing Azure resources?",
  ["Azure Portal", "Azure CLI only", "PowerShell only", "ARM template compiler only"],
  0,
  "The Azure Portal is the web UI for creating and managing resources.",
  "https://learn.microsoft.com/en-us/training/modules/describe-features-tools-manage-deploy-azure-resources/2-describe-azure-portal"
);
add(
  AM,
  "Azure Cloud Shell provides:",
  ["A browser-accessible shell with Azure CLI and PowerShell", "Physical rack management", "On-premises Hyper-V console", "A replacement for Azure AD tenants"],
  0,
  "Cloud Shell runs CLI tools from the browser without local installs.",
  "https://learn.microsoft.com/en-us/training/modules/describe-features-tools-manage-deploy-azure-resources/4-describe-azure-cloud-shell"
);
add(
  AM,
  "Azure Advisor recommendations focus on:",
  ["Cost, security, reliability, operational excellence, and performance", "Only marketing campaigns", "Deleting all unused resources automatically without review", "Replacing SLAs"],
  0,
  "Advisor analyzes configurations and usage to suggest improvements across five pillars.",
  "https://learn.microsoft.com/en-us/training/modules/describe-monitoring-tools/3-describe-azure-advisor"
);
add(
  AM,
  "Azure Monitor is primarily for:",
  ["Collecting metrics, logs, and telemetry for observability", "Domain registration", "Blob tiering only", "Creating AD groups only"],
  0,
  "Monitor aggregates data for alerting, dashboards, and diagnostics.",
  "https://learn.microsoft.com/en-us/training/modules/describe-monitoring-tools/2-describe-azure-monitor"
);
add(
  AM,
  "Azure Service Health notifies you about:",
  ["Platform incidents, planned maintenance, and health advisories affecting your services", "Individual user password expirations only", "GitHub pull requests", "Local PC antivirus status"],
  0,
  "Service Health communicates Azure platform events relevant to your resources.",
  "https://learn.microsoft.com/en-us/training/modules/describe-monitoring-tools/4-describe-azure-service-health"
);
add(
  AM,
  "Role-Based Access Control (RBAC) assigns permissions based on:",
  ["Roles, scopes, and assignments to identities", "Physical location of the user only", "Random token generation", "Storage account tier"],
  0,
  "RBAC grants actions on scopes via role assignments.",
  "https://learn.microsoft.com/en-us/training/modules/describe-basic-security-features/3-describe-role-based-access-control"
);
add(
  AM,
  "Microsoft Entra ID (Azure AD) provides:",
  ["Identity and access management for users and applications", "Blob lifecycle management", "VPN gateway termination only", "SQL query optimization"],
  0,
  "Entra ID handles authentication, SSO, and identity protection for cloud apps.",
  "https://learn.microsoft.com/en-us/training/modules/describe-basic-security-features/2-describe-azure-active-directory"
);
add(
  AM,
  "Multi-factor authentication (MFA) adds security by:",
  ["Requiring multiple forms of verification such as password plus phone or authenticator", "Disabling encryption", "Removing audit logs", "Using one shared admin password"],
  0,
  "MFA combines something you know with something you have or are.",
  "https://learn.microsoft.com/en-us/training/modules/describe-basic-security-features/4-describe-multi-factor-authentication"
);
add(
  AM,
  "Azure Cost Management helps you to:",
  ["Analyze spending, set budgets, and optimize cloud costs", "Automatically delete all VMs nightly", "Disable all SLAs", "Replace Azure Policy"],
  0,
  "Cost Management provides reporting, budgets, and recommendations for spend control.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cost-management/2-describe-cost-management"
);
add(
  AM,
  "Which Azure governance scope is at the top of the hierarchy?",
  ["Resource", "Resource group", "Subscription", "Management group"],
  3,
  "Management groups sit above subscriptions to organize policies and access at scale.",
  "https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/5-describe-subscriptions"
);
add(
  AM,
  "An Azure resource group is:",
  ["A container that holds related resources for lifecycle management", "A type of VM SKU", "A DNS record set", "A certificate authority"],
  0,
  "Resource groups bundle resources that share the same lifecycle.",
  "https://learn.microsoft.com/en-us/training/modules/describe-core-architectural-components-of-azure/5-describe-subscriptions"
);
add(
  AM,
  "Tags in Azure are used to:",
  ["Apply metadata such as cost center or environment for organization and billing", "Encrypt disks by default", "Increase VM CPU automatically", "Replace RBAC"],
  0,
  "Tags are key-value metadata for reporting and automation.",
  "https://learn.microsoft.com/en-us/training/modules/describe-features-tools-manage-deploy-azure-resources/5-describe-tags"
);
add(
  AM,
  "The Azure Well-Architected Framework includes pillars such as:",
  ["Reliability, security, cost optimization, operational excellence, and performance efficiency", "Only marketing and sales", "Hardware manufacturing", "Desktop antivirus"],
  0,
  "The five pillars guide design decisions for cloud workloads on Azure.",
  "https://learn.microsoft.com/en-us/training/modules/describe-monitoring-tools/5-describe-azure-well-architected-framework"
);
add(
  AM,
  "Azure CLI is:",
  ["A cross-platform command-line tool for managing Azure resources", "A graphical BI dashboard only", "A VM extension for antivirus", "An alternative to all SLAs"],
  0,
  "Azure CLI commands automate resource management from terminals and scripts.",
  "https://learn.microsoft.com/en-us/training/modules/describe-features-tools-manage-deploy-azure-resources/6-describe-azure-cli"
);
add(
  AM,
  "PowerShell in Azure is often used to:",
  ["Automate administration using cmdlets and scripts", "Physically rack servers", "Replace Azure regions", "Disable monitoring"],
  0,
  "Azure PowerShell modules automate deployment and management tasks.",
  "https://learn.microsoft.com/en-us/training/modules/describe-features-tools-manage-deploy-azure-resources/7-describe-azure-powershell"
);
add(
  AM,
  "Azure Resource Locks can prevent:",
  ["Accidental deletion or modification of critical resources", "All read operations globally", "Any tagging", "Network traffic entirely"],
  0,
  "Locks apply CanNotDelete or ReadOnly protection at scopes.",
  "https://learn.microsoft.com/en-us/training/modules/describe-features-tools-manage-deploy-azure-resources/8-describe-resource-locks"
);
add(
  AM,
  "Total Cost of Ownership (TCO) calculator helps you:",
  ["Estimate cost savings of moving workloads to Azure versus on-premises", "Generate ARM templates automatically", "Create AD users in bulk only", "Monitor application traces"],
  0,
  "The TCO calculator compares on-premises costs with Azure estimates.",
  "https://learn.microsoft.com/en-us/training/modules/describe-cost-management/3-describe-total-cost-ownership-calculator"
);
add(
  AM,
  "Compliance offerings in Azure documentation help you:",
  ["Understand regulatory certifications and compliance responsibilities", "Remove all logging", "Avoid SLAs", "Disable encryption"],
  0,
  "Trust Center and compliance docs map Azure certifications to customer obligations.",
  "https://learn.microsoft.com/en-us/training/modules/describe-security-privacy-compliance-trust/7-describe-compliance-offerings"
);

mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, JSON.stringify(questions, null, 2));
console.log(`Wrote ${questions.length} questions to ${out}`);
console.log("Next: python scripts/merge_extra_questions.py && python scripts/sync_study_urls.py && python scripts/resync_questions.py");
