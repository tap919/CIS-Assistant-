#!/usr/bin/env python3
"""
CIS Assistant MCP Server

This server provides tools for LLM-augmented code development using the
Circulatory Informatics System (CIS) methodology, enhanced with blockchain
automation for the Base layer 2 platform.

The server integrates the Circulatory Informatics Bible to maintain adherence
to CIS structure, provides aids for common LLM coding issues, and serves as
a bridge between supply chain management, blockchain technology, and small
business adoption on the Base L2 network.
"""

import asyncio
import ast
import json
import uuid
import re
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
)
class CISAssistantServer:
    """
    MCP Server for CIS Assistant

    Provides tools for:
    - Contract generation for software components
    - Code implementation with validation
    - Constraint checking
    - Adaptive example management
    - Error pattern analysis
    - Circulatory Informatics methodology guidance
    - Common LLM coding issue aids
    - Base L2 blockchain automation and network information
    - Supply chain smart contract generation and validation
    - Small business blockchain onboarding guidance
    - Supplier intelligence: financial health, geopolitical risk, lead time variance, ESG scoring
    - Multi-modal carrier visibility: normalized tracking schema across FedEx, UPS, Maersk, DHL
    - Cross-ERP context bridge: field mapping between SAP, Oracle Fusion, NetSuite, Dynamics 365
    - Continuous planning: rolling demand sensing, inventory optimization, constraint management, S&OP
    - Sustainability: Scope 3 carbon calculation, modal comparison, carbon-aware routing

    Note: This implementation uses in-memory storage. All contracts, patterns,
    and examples will be lost when the server restarts. For production use,
    consider implementing persistent storage using files or a database.
    """
    
    # Constants for code truncation
    MAX_CODE_SNIPPET_LENGTH = 500
    MAX_BEFORE_AFTER_LENGTH = 200
    MAX_BIBLE_SECTION_LENGTH = 5000
    
    # Common LLM coding issues and their solutions
    LLM_CODING_AIDS = {
        "context_window_overflow": {
            "description": "LLM loses context with large codebases",
            "solutions": [
                "Break code into smaller, focused modules",
                "Use progressive context loading (start with interfaces, add details)",
                "Summarize distant context before providing detail",
                "Use adaptive token budgeting - prioritize most relevant context"
            ]
        },
        "hallucinated_imports": {
            "description": "LLM invents non-existent libraries or APIs",
            "solutions": [
                "Always verify imports exist before using them",
                "Provide explicit list of available dependencies",
                "Include actual import statements from working code as examples",
                "Cross-reference with requirements.txt or package.json"
            ]
        },
        "inconsistent_naming": {
            "description": "LLM uses inconsistent naming conventions across code",
            "solutions": [
                "Provide explicit naming convention rules upfront",
                "Include examples of correct naming in context",
                "Use constraint checklists that specify naming patterns",
                "Review generated code for naming consistency before execution"
            ]
        },
        "missing_error_handling": {
            "description": "LLM omits try/except blocks and edge case handling",
            "solutions": [
                "Explicitly require error handling in contracts",
                "Provide examples with comprehensive error handling",
                "Add validation rules that check for exception handling",
                "Include 'graceful degradation' as a behavioral constraint"
            ]
        },
        "type_hint_inconsistency": {
            "description": "LLM provides incomplete or incorrect type hints",
            "solutions": [
                "Enforce type hints through validation rules",
                "Provide type hint examples for complex types",
                "Use TypedDict and Protocol examples for clarity",
                "Validate with mypy or similar tools"
            ]
        },
        "incomplete_implementation": {
            "description": "LLM provides stub implementations or 'pass' statements",
            "solutions": [
                "Require complete implementations in constraints",
                "Validate that no 'pass' or 'TODO' remains",
                "Use progressive example complexity (simple → complete)",
                "Check for stub patterns in validation"
            ]
        },
        "security_vulnerabilities": {
            "description": "LLM generates code with common security issues",
            "solutions": [
                "Include security constraints in contracts",
                "Validate input sanitization and parameterized queries",
                "Check for hardcoded secrets patterns",
                "Require secure defaults in configuration"
            ]
        },
        "logic_drift": {
            "description": "LLM solution drifts from original intent over iterations",
            "solutions": [
                "Maintain explicit contract reference throughout",
                "Use checkpoints to preserve known-good states",
                "Re-state original requirements when iterating",
                "Compare current solution against initial constraints"
            ]
        }
    }
    
    # CIS Seven Principles for methodology adherence
    CIS_SEVEN_PRINCIPLES = {
        "distributed_autonomy": {
            "principle": "No single point of control. Each 'organ' operates autonomously within a decentralized governance framework.",
            "implication": "Services should make decisions without asking permission from a central authority. Use event-driven pub/sub patterns.",
            "code_pattern": "Decouple components, use message queues, avoid synchronous dependencies"
        },
        "continuous_sensing": {
            "principle": "The organism must continuously monitor its own state through events.",
            "implication": "Observability isn't optional—it's part of the organism's nervous system. Every event is a data point.",
            "code_pattern": "Add logging, metrics, and health checks to all components"
        },
        "feedback_driven_adaptation": {
            "principle": "Adaptation requires feedback loops that measure deviation and trigger corrective action.",
            "implication": "Self-healing and auto-remediation are baseline expectations, not optional features.",
            "code_pattern": "Implement retry logic, circuit breakers, and automatic recovery mechanisms"
        },
        "emergent_intelligence": {
            "principle": "Intelligence emerges from interaction of simple agents following local rules.",
            "implication": "Don't create one super-intelligent controller. Create multiple specialized agents that collaborate.",
            "code_pattern": "Design small, focused components that communicate through well-defined interfaces"
        },
        "memory_and_learning": {
            "principle": "The organism learns from past events and adjusts future behavior.",
            "implication": "Pattern analysis and learning from history aren't optional—they're how the system improves.",
            "code_pattern": "Record error patterns, track successful fixes, build adaptive example libraries"
        },
        "graceful_degradation": {
            "principle": "No single component is essential. The system continues functioning when components fail.",
            "implication": "Design for fault tolerance at every level. Failures should not cascade.",
            "code_pattern": "Use fallbacks, timeouts, and isolation patterns to prevent cascading failures"
        },
        "efficient_resource_flow": {
            "principle": "Resources flow to where they're needed. Demand drives allocation.",
            "implication": "Auto-scaling, load balancing, and resource optimization are structural requirements.",
            "code_pattern": "Implement resource pooling, lazy loading, and demand-based scaling"
        }
    }

    # Base L2 Network Configuration
    BASE_NETWORK_CONFIG = {
        "mainnet": {
            "name": "Base Mainnet",
            "chain_id": 8453,
            "rpc_url": "https://mainnet.base.org",
            "block_explorer": "https://basescan.org",
            "bridge": "https://bridge.base.org",
            "currency": "ETH",
            "layer": "L2 (Optimistic Rollup on Ethereum)",
            "avg_block_time": "2 seconds",
            "avg_gas_cost": "< $0.01 USD",
            "description": "Base is a secure, low-cost, builder-friendly Ethereum L2 built to bring the next billion users onchain.",
        },
        "sepolia": {
            "name": "Base Sepolia (Testnet)",
            "chain_id": 84532,
            "rpc_url": "https://sepolia.base.org",
            "block_explorer": "https://sepolia.basescan.org",
            "bridge": "https://bridge.base.org",
            "currency": "ETH (Testnet)",
            "layer": "L2 Testnet (Optimistic Rollup on Ethereum Sepolia)",
            "avg_block_time": "2 seconds",
            "avg_gas_cost": "Free (testnet)",
            "description": "Base Sepolia testnet for development and testing.",
        },
    }

    # Supply Chain Smart Contract Templates
    SUPPLY_CHAIN_TEMPLATES = {
        "product_tracking": {
            "name": "Product Tracking",
            "description": "Track products through the supply chain with provenance verification",
            "use_cases": [
                "Food safety and traceability",
                "Pharmaceutical tracking",
                "Manufacturing parts tracking",
                "Retail inventory management",
            ],
            "solidity_template": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ProductTracking
 * @dev Track products through supply chain stages on Base L2
 * @notice Low gas costs on Base make per-item tracking economically viable
 */
contract ProductTracking {
    enum Stage { Created, InTransit, Delivered, Verified }

    struct Product {
        uint256 id;
        string name;
        string origin;
        address currentHolder;
        Stage stage;
        uint256 createdAt;
        uint256 updatedAt;
    }

    mapping(uint256 => Product) public products;
    mapping(uint256 => address[]) public productHistory;
    uint256 public productCount;

    event ProductCreated(uint256 indexed id, string name, string origin, address creator);
    event ProductTransferred(uint256 indexed id, address indexed from, address indexed to, Stage stage);
    event ProductVerified(uint256 indexed id, address verifier);

    modifier onlyHolder(uint256 _productId) {
        require(products[_productId].currentHolder == msg.sender, "Not current holder");
        _;
    }

    function createProduct(string memory _name, string memory _origin) external returns (uint256) {
        productCount++;
        products[productCount] = Product({
            id: productCount,
            name: _name,
            origin: _origin,
            currentHolder: msg.sender,
            stage: Stage.Created,
            createdAt: block.timestamp,
            updatedAt: block.timestamp
        });
        productHistory[productCount].push(msg.sender);
        emit ProductCreated(productCount, _name, _origin, msg.sender);
        return productCount;
    }

    function transferProduct(uint256 _productId, address _to) external onlyHolder(_productId) {
        Product storage product = products[_productId];
        product.currentHolder = _to;
        product.stage = Stage.InTransit;
        product.updatedAt = block.timestamp;
        productHistory[_productId].push(_to);
        emit ProductTransferred(_productId, msg.sender, _to, Stage.InTransit);
    }

    function confirmDelivery(uint256 _productId) external onlyHolder(_productId) {
        Product storage product = products[_productId];
        product.stage = Stage.Delivered;
        product.updatedAt = block.timestamp;
        emit ProductTransferred(_productId, msg.sender, msg.sender, Stage.Delivered);
    }

    function verifyProduct(uint256 _productId) external onlyHolder(_productId) {
        Product storage product = products[_productId];
        product.stage = Stage.Verified;
        product.updatedAt = block.timestamp;
        emit ProductVerified(_productId, msg.sender);
    }

    function getProductHistory(uint256 _productId) external view returns (address[] memory) {
        return productHistory[_productId];
    }
}''',
        },
        "supplier_registry": {
            "name": "Supplier Registry",
            "description": "Decentralized registry for verified suppliers and vendors",
            "use_cases": [
                "Vendor onboarding and verification",
                "Supplier reputation tracking",
                "B2B marketplace trust layer",
                "Small business discovery",
            ],
            "solidity_template": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title SupplierRegistry
 * @dev Decentralized supplier registry for Base L2 supply chain
 * @notice Enables small businesses to build on-chain reputation
 */
contract SupplierRegistry {
    struct Supplier {
        address wallet;
        string businessName;
        string category;
        string location;
        uint256 registeredAt;
        uint256 completedOrders;
        uint256 rating;  // 0-500 scale (0 = unrated, 1-500 for scored suppliers)
        bool verified;
        bool active;
    }

    mapping(address => Supplier) public suppliers;
    address[] public supplierList;
    mapping(address => bool) public verifiers;
    address public owner;

    event SupplierRegistered(address indexed supplier, string businessName, string category);
    event SupplierVerified(address indexed supplier, address indexed verifier);
    event OrderCompleted(address indexed supplier, uint256 totalOrders);
    event RatingUpdated(address indexed supplier, uint256 newRating);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyVerifier() {
        require(verifiers[msg.sender], "Not a verifier");
        _;
    }

    constructor() {
        owner = msg.sender;
        verifiers[msg.sender] = true;
    }

    function registerSupplier(
        string memory _businessName,
        string memory _category,
        string memory _location
    ) external {
        require(suppliers[msg.sender].wallet == address(0), "Already registered");
        suppliers[msg.sender] = Supplier({
            wallet: msg.sender,
            businessName: _businessName,
            category: _category,
            location: _location,
            registeredAt: block.timestamp,
            completedOrders: 0,
            rating: 0,
            verified: false,
            active: true
        });
        supplierList.push(msg.sender);
        emit SupplierRegistered(msg.sender, _businessName, _category);
    }

    function verifySupplier(address _supplier) external onlyVerifier {
        require(suppliers[_supplier].wallet != address(0), "Supplier not found");
        suppliers[_supplier].verified = true;
        emit SupplierVerified(_supplier, msg.sender);
    }

    function recordCompletedOrder(address _supplier) external onlyVerifier {
        require(suppliers[_supplier].wallet != address(0), "Supplier not found");
        suppliers[_supplier].completedOrders++;
        emit OrderCompleted(_supplier, suppliers[_supplier].completedOrders);
    }

    function updateRating(address _supplier, uint256 _rating) external onlyVerifier {
        require(_rating <= 500, "Rating must be 0-500");
        require(suppliers[_supplier].wallet != address(0), "Supplier not found");
        suppliers[_supplier].rating = _rating;
        emit RatingUpdated(_supplier, _rating);
    }

    function addVerifier(address _verifier) external onlyOwner {
        verifiers[_verifier] = true;
    }

    function getSupplierCount() external view returns (uint256) {
        return supplierList.length;
    }
}''',
        },
        "invoice_management": {
            "name": "Invoice Management",
            "description": "On-chain invoice creation, tracking, and payment verification",
            "use_cases": [
                "B2B payment tracking",
                "Invoice factoring and financing",
                "Automated payment verification",
                "Small business cash flow management",
            ],
            "solidity_template": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title InvoiceManagement
 * @dev On-chain invoice management for Base L2 supply chain
 * @notice Enables transparent B2B payment tracking for small businesses
 */
contract InvoiceManagement {
    enum InvoiceStatus { Created, Sent, Paid, Disputed, Resolved }

    struct Invoice {
        uint256 id;
        address issuer;
        address payer;
        uint256 amount;
        string description;
        InvoiceStatus status;
        uint256 createdAt;
        uint256 dueDate;
        uint256 paidAt;
    }

    mapping(uint256 => Invoice) public invoices;
    mapping(address => uint256[]) public issuerInvoices;
    mapping(address => uint256[]) public payerInvoices;
    uint256 public invoiceCount;

    event InvoiceCreated(uint256 indexed id, address indexed issuer, address indexed payer, uint256 amount);
    event InvoicePaid(uint256 indexed id, address indexed payer, uint256 amount);
    event InvoiceDisputed(uint256 indexed id, address indexed disputer);
    event InvoiceResolved(uint256 indexed id);

    function createInvoice(
        address _payer,
        uint256 _amount,
        string memory _description,
        uint256 _dueDate
    ) external returns (uint256) {
        require(_payer != address(0), "Invalid payer address");
        require(_amount > 0, "Amount must be positive");
        require(_dueDate > block.timestamp, "Due date must be in the future");

        invoiceCount++;
        invoices[invoiceCount] = Invoice({
            id: invoiceCount,
            issuer: msg.sender,
            payer: _payer,
            amount: _amount,
            description: _description,
            status: InvoiceStatus.Created,
            createdAt: block.timestamp,
            dueDate: _dueDate,
            paidAt: 0
        });
        issuerInvoices[msg.sender].push(invoiceCount);
        payerInvoices[_payer].push(invoiceCount);
        emit InvoiceCreated(invoiceCount, msg.sender, _payer, _amount);
        return invoiceCount;
    }

    function payInvoice(uint256 _invoiceId) external payable {
        Invoice storage invoice = invoices[_invoiceId];
        require(invoice.payer == msg.sender, "Not the designated payer");
        require(invoice.status == InvoiceStatus.Created || invoice.status == InvoiceStatus.Sent, "Invoice not payable");
        require(msg.value == invoice.amount, "Incorrect payment amount");

        invoice.status = InvoiceStatus.Paid;
        invoice.paidAt = block.timestamp;

        (bool sent, ) = payable(invoice.issuer).call{value: msg.value}("");
        require(sent, "Payment transfer failed");

        emit InvoicePaid(_invoiceId, msg.sender, msg.value);
    }

    function disputeInvoice(uint256 _invoiceId) external {
        Invoice storage invoice = invoices[_invoiceId];
        require(
            msg.sender == invoice.payer || msg.sender == invoice.issuer,
            "Not a party to this invoice"
        );
        require(invoice.status != InvoiceStatus.Paid, "Already paid");
        invoice.status = InvoiceStatus.Disputed;
        emit InvoiceDisputed(_invoiceId, msg.sender);
    }
}''',
        },
        "certification_nft": {
            "name": "Certification NFT",
            "description": "Issue and verify supply chain certifications as NFTs",
            "use_cases": [
                "Quality certifications (ISO, organic, fair trade)",
                "Compliance and audit records",
                "Business license verification",
                "Training and credential tracking",
            ],
            "solidity_template": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title CertificationNFT
 * @dev Issue supply chain certifications as NFTs on Base L2
 * @notice Low-cost certification issuance for small business compliance
 */
contract CertificationNFT {
    struct Certification {
        uint256 id;
        address issuer;
        address holder;
        string certType;
        string details;
        uint256 issuedAt;
        uint256 expiresAt;
        bool revoked;
    }

    mapping(uint256 => Certification) public certifications;
    mapping(address => uint256[]) public holderCerts;
    mapping(address => bool) public authorizedIssuers;
    uint256 public certCount;
    address public owner;

    event CertificationIssued(uint256 indexed id, address indexed holder, string certType);
    event CertificationRevoked(uint256 indexed id, address indexed revoker);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyAuthorizedIssuer() {
        require(authorizedIssuers[msg.sender], "Not authorized issuer");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true;
    }

    function issueCertification(
        address _holder,
        string memory _certType,
        string memory _details,
        uint256 _expiresAt
    ) external onlyAuthorizedIssuer returns (uint256) {
        certCount++;
        certifications[certCount] = Certification({
            id: certCount,
            issuer: msg.sender,
            holder: _holder,
            certType: _certType,
            details: _details,
            issuedAt: block.timestamp,
            expiresAt: _expiresAt,
            revoked: false
        });
        holderCerts[_holder].push(certCount);
        emit CertificationIssued(certCount, _holder, _certType);
        return certCount;
    }

    function revokeCertification(uint256 _certId) external onlyAuthorizedIssuer {
        require(certifications[_certId].issuer == msg.sender, "Not the issuer");
        certifications[_certId].revoked = true;
        emit CertificationRevoked(_certId, msg.sender);
    }

    function verifyCertification(uint256 _certId) external view returns (bool valid, string memory certType) {
        Certification memory cert = certifications[_certId];
        // expiresAt == 0 means the certification never expires
        valid = !cert.revoked && (cert.expiresAt == 0 || cert.expiresAt > block.timestamp);
        certType = cert.certType;
    }

    function addAuthorizedIssuer(address _issuer) external onlyOwner {
        authorizedIssuers[_issuer] = true;
    }

    function getHolderCertifications(address _holder) external view returns (uint256[] memory) {
        return holderCerts[_holder];
    }
}''',
        },
    }

    # Business Onboarding Guides
    BUSINESS_ONBOARDING = {
        "getting_started": {
            "title": "Getting Started with Blockchain for Your Business",
            "steps": [
                "1. **Understand the Value**: Blockchain on Base L2 provides transparent, immutable records at very low cost (< $0.01 per transaction)",
                "2. **Set Up a Wallet**: Create a business wallet using MetaMask or Coinbase Wallet - this is your on-chain identity",
                "3. **Get Test ETH**: Start on Base Sepolia testnet to experiment without spending real funds",
                "4. **Choose Your Use Case**: Select from product tracking, supplier management, invoicing, or certifications",
                "5. **Deploy Your First Contract**: Use the CIS Assistant to generate and deploy your first smart contract",
                "6. **Integrate with Your Workflow**: Connect blockchain records to your existing business processes",
            ],
        },
        "cost_analysis": {
            "title": "Cost Analysis: Base L2 for Small Businesses",
            "details": [
                "**Transaction Costs**: < $0.01 per transaction on Base (vs $5-50 on Ethereum mainnet)",
                "**Contract Deployment**: Typically $0.10-$1.00 on Base (vs $50-500 on Ethereum mainnet)",
                "**Monthly Operating Costs**: Estimated $5-$50/month for typical small business usage",
                "**Comparison**: Traditional supply chain software costs $200-$2000/month",
                "**No Subscription Fees**: Smart contracts run without ongoing platform fees",
                "**Pay-per-Use Model**: Only pay gas for transactions you actually make",
            ],
        },
        "use_case_guide": {
            "title": "Supply Chain Use Cases for Small Businesses",
            "use_cases": {
                "retail": {
                    "description": "Track inventory, verify product authenticity, manage supplier relationships",
                    "recommended_contracts": ["product_tracking", "supplier_registry"],
                    "estimated_setup_time": "1-2 weeks",
                },
                "food_beverage": {
                    "description": "Farm-to-table traceability, temperature logging, organic certification verification",
                    "recommended_contracts": ["product_tracking", "certification_nft"],
                    "estimated_setup_time": "2-3 weeks",
                },
                "manufacturing": {
                    "description": "Parts tracking, quality control records, supplier qualification management",
                    "recommended_contracts": ["product_tracking", "supplier_registry", "certification_nft"],
                    "estimated_setup_time": "3-4 weeks",
                },
                "services": {
                    "description": "Invoice management, service delivery verification, credential tracking",
                    "recommended_contracts": ["invoice_management", "certification_nft"],
                    "estimated_setup_time": "1-2 weeks",
                },
                "wholesale_distribution": {
                    "description": "Bulk shipment tracking, B2B payments, vendor management",
                    "recommended_contracts": ["product_tracking", "invoice_management", "supplier_registry"],
                    "estimated_setup_time": "2-3 weeks",
                },
            },
        },
        "integration_guide": {
            "title": "Integrating Blockchain with Existing Business Systems",
            "steps": [
                "1. **Identify Data Points**: Determine which business events should be recorded on-chain",
                "2. **Choose Integration Method**: REST API wrapper, webhook triggers, or direct Web3 integration",
                "3. **Set Up Event Listeners**: Monitor blockchain events to update your existing systems",
                "4. **Implement Gradual Migration**: Start with one process (e.g., invoicing) before expanding",
                "5. **Train Your Team**: Ensure staff understand wallet management and basic blockchain concepts",
                "6. **Monitor and Optimize**: Use Base block explorer to monitor transactions and optimize gas usage",
            ],
            "recommended_tools": [
                "**Web3.py / ethers.js**: Libraries for interacting with Base from your applications",
                "**Hardhat / Foundry**: Development frameworks for deploying and testing smart contracts",
                "**The Graph**: Indexing protocol for querying blockchain data efficiently",
                "**OpenZeppelin**: Audited smart contract libraries for secure development",
                "**Alchemy / Infura**: Node providers for reliable Base L2 connectivity",
            ],
        },
    }

    # ---------------------------------------------------------------------------
    # Supplier Intelligence Data
    # ---------------------------------------------------------------------------
    SUPPLIER_RISK_FACTORS = {
        "financial_health": {
            "title": "Financial Health Indicators",
            "signals": [
                "Credit rating changes (Moody's, S&P, Fitch)",
                "Debt-to-equity ratio trends",
                "Days payable outstanding (DPO) drift",
                "Cash flow from operations year-over-year",
                "Revenue concentration risk (single customer >30%)",
                "Accounts receivable aging",
            ],
            "risk_levels": {
                "low": "Stable credit, healthy cash flow, diversified revenue",
                "medium": "Minor credit watch, cash flow volatility, moderate concentration",
                "high": "Credit downgrade, negative cash flow, >50% revenue concentration",
                "critical": "Bankruptcy filing, payment defaults, business continuity risk",
            },
            "data_sources": ["Dun & Bradstreet", "Coface", "Everstream Analytics", "SEC filings"],
        },
        "geopolitical_exposure": {
            "title": "Geopolitical & Country Risk",
            "signals": [
                "Country political stability index (World Bank)",
                "Trade tariff and embargo exposure",
                "Currency volatility (FX risk)",
                "Natural disaster frequency (region risk score)",
                "Labor unrest and strike history",
                "Sanctions list monitoring (OFAC, EU, UN)",
            ],
            "risk_levels": {
                "low": "OECD stable country, no sanctions exposure, minimal FX risk",
                "medium": "Developing market, moderate tariff exposure, some FX volatility",
                "high": "Politically unstable region, tariff escalation risk, high FX",
                "critical": "Active conflict zone, sanctions risk, supply route disruption",
            },
            "data_sources": ["Riskmethods", "World Bank Governance Indicators", "OFAC", "Everstream"],
        },
        "lead_time_variance": {
            "title": "Lead Time & Delivery Performance",
            "signals": [
                "On-time delivery rate (OTD%) rolling 90 days",
                "Lead time mean and standard deviation",
                "Expedite frequency (% of orders requiring rush)",
                "Carrier transit time variance by lane",
                "Port congestion index for origin/destination",
                "Order fill rate and backorder rate",
            ],
            "risk_levels": {
                "low": "OTD >95%, lead time variance <10%, no port congestion",
                "medium": "OTD 85-95%, lead time variance 10-25%, minor port delays",
                "high": "OTD 70-85%, lead time variance >25%, active port congestion",
                "critical": "OTD <70%, chronic delays, supply stoppage risk",
            },
            "data_sources": ["ERP order history", "TMS carrier data", "Port authority APIs", "FourKites"],
        },
        "esg_scores": {
            "title": "Environmental, Social & Governance (ESG)",
            "signals": [
                "Carbon emissions intensity (Scope 1, 2, 3)",
                "Water usage and waste generation",
                "Labor standards compliance (ILO conventions)",
                "Diversity and inclusion metrics",
                "Governance transparency score",
                "Third-party ESG audit results (EcoVadis, CDP)",
            ],
            "risk_levels": {
                "low": "EcoVadis Gold/Platinum, CDP A-list, certified labor standards",
                "medium": "EcoVadis Silver, CDP B-list, minor labor compliance gaps",
                "high": "EcoVadis Bronze, unverified emissions, labor concerns",
                "critical": "No ESG program, regulatory violations, reputational risk",
            },
            "data_sources": ["EcoVadis", "CDP", "Sustainalytics", "MSCI ESG"],
        },
    }

    # ---------------------------------------------------------------------------
    # Multi-Modal Carrier Visibility Data
    # ---------------------------------------------------------------------------
    CARRIER_APIS = {
        "fedex": {
            "name": "FedEx",
            "api_version": "v1",
            "auth": "OAuth 2.0 (client_credentials)",
            "base_url": "https://apis.fedex.com",
            "key_endpoints": {
                "tracking": "/track/v1/trackingnumbers",
                "rates": "/rate/v1/rates/quotes",
                "pickup": "/pickup/v1/pickups",
                "ship": "/ship/v1/shipments",
            },
            "tracking_fields": ["trackingNumber", "status", "statusByLocale", "dateAndTimes",
                                 "estimatedDeliveryTimeWindow", "packageDetails", "events"],
            "modes": ["express", "ground", "freight", "international"],
            "webhook_support": True,
            "normalized_status_map": {
                "OC": "order_created", "PU": "picked_up", "IT": "in_transit",
                "OD": "out_for_delivery", "DL": "delivered", "DE": "exception",
            },
        },
        "ups": {
            "name": "UPS",
            "api_version": "v1",
            "auth": "OAuth 2.0 (client_credentials)",
            "base_url": "https://onlinetools.ups.com/api",
            "key_endpoints": {
                "tracking": "/track/v1/details/{inquiryNumber}",
                "rates": "/rating/v1/shop",
                "pickup": "/pickupcreation/v2/pickup",
                "ship": "/shipments/v1/ship",
            },
            "tracking_fields": ["trackingNumber", "currentStatus", "currentStatusDescription",
                                 "scheduledDelivery", "deliveryDate", "activity"],
            "modes": ["ground", "air", "international", "freight"],
            "webhook_support": True,
            "normalized_status_map": {
                "M": "order_created", "P": "picked_up", "I": "in_transit",
                "O": "out_for_delivery", "D": "delivered", "X": "exception",
            },
        },
        "maersk": {
            "name": "Maersk (Ocean Freight)",
            "api_version": "v2",
            "auth": "API Key",
            "base_url": "https://api.maersk.com",
            "key_endpoints": {
                "tracking": "/shipments/{shipmentId}",
                "schedules": "/schedules/vessel-schedules",
                "rates": "/rates",
                "booking": "/bookings",
            },
            "tracking_fields": ["shipmentId", "transportPlan", "containers", "milestones",
                                 "estimatedArrival", "vesselName", "voyageNumber"],
            "modes": ["ocean_fcl", "ocean_lcl", "intermodal"],
            "webhook_support": True,
            "normalized_status_map": {
                "BOOKED": "order_created", "GATED_IN": "picked_up", "VESSEL_DEPARTED": "in_transit",
                "VESSEL_ARRIVED": "in_transit", "GATED_OUT": "out_for_delivery", "DELIVERED": "delivered",
            },
        },
        "dhl": {
            "name": "DHL Express",
            "api_version": "v2",
            "auth": "Basic Auth / API Key",
            "base_url": "https://api-eu.dhl.com",
            "key_endpoints": {
                "tracking": "/track/shipments?trackingNumber={trackingNumber}",
                "rates": "/rates",
                "pickup": "/pickups",
                "ship": "/shipments",
            },
            "tracking_fields": ["id", "description", "status", "timestamp", "location", "events"],
            "modes": ["express", "parcel", "freight", "ecommerce"],
            "webhook_support": True,
            "normalized_status_map": {
                "pre-transit": "order_created", "transit": "in_transit",
                "delivered": "delivered", "failure": "exception", "unknown": "unknown",
            },
        },
    }

    NORMALIZED_TRACKING_SCHEMA = {
        "shipment_id": "Unique identifier for the shipment",
        "carrier": "Carrier name (fedex, ups, maersk, dhl, etc.)",
        "tracking_number": "Carrier-specific tracking number",
        "origin": {"address": "str", "city": "str", "state": "str", "country": "str", "postal_code": "str"},
        "destination": {"address": "str", "city": "str", "state": "str", "country": "str", "postal_code": "str"},
        "status": "Normalized status: order_created | picked_up | in_transit | out_for_delivery | delivered | exception",
        "estimated_delivery": "ISO 8601 datetime string",
        "actual_delivery": "ISO 8601 datetime string or null",
        "events": [{"timestamp": "ISO 8601", "location": "str", "status": "normalized status", "description": "str"}],
        "mode": "transport mode: express | ground | ocean_fcl | ocean_lcl | air | freight | intermodal",
        "weight_kg": "float",
        "dimensions_cm": {"length": "float", "width": "float", "height": "float"},
        "service_level": "str",
        "carbon_kg_co2e": "Estimated CO2 equivalent for this shipment (float)",
    }

    # ---------------------------------------------------------------------------
    # Cross-ERP Context Bridge Data
    # ---------------------------------------------------------------------------
    ERP_SYSTEMS = {
        "sap": {
            "name": "SAP S/4HANA",
            "modules": ["MM (Materials Management)", "SD (Sales & Distribution)", "WM (Warehouse Management)",
                        "PP (Production Planning)", "FI (Financial Accounting)", "CO (Controlling)",
                        "EWM (Extended Warehouse Management)", "TM (Transportation Management)"],
            "key_objects": {
                "purchase_order": {"object": "Purchase Order (ME21N)", "table": "EKKO/EKPO", "idoc": "ORDERS05"},
                "sales_order": {"object": "Sales Order (VA01)", "table": "VBAK/VBAP", "idoc": "ORDERS05"},
                "goods_receipt": {"object": "Goods Receipt (MIGO)", "table": "MKPF/MSEG", "idoc": "DESADV"},
                "invoice": {"object": "Vendor Invoice (MIRO)", "table": "RBKP/RSEG", "idoc": "INVOIC02"},
                "material": {"object": "Material Master (MM60)", "table": "MARA/MARC", "idoc": "MATMAS05"},
                "vendor": {"object": "Vendor Master (XK01)", "table": "LFA1/LFB1", "idoc": "CREMAS05"},
            },
            "integration_protocols": ["IDoc", "BAPI", "RFC", "OData (REST)", "SOAP"],
            "mcp_approach": "Use SAP OData services via /sap/opu/odata/ namespace for real-time reads",
        },
        "oracle": {
            "name": "Oracle Fusion SCM / ERP Cloud",
            "modules": ["Order Management", "Inventory Management", "Procurement", "Warehouse Management",
                        "Transportation Management", "Manufacturing", "Financial Management"],
            "key_objects": {
                "purchase_order": {"object": "Purchase Order", "api": "purchaseOrders", "rest": "/fscmRestApi/resources/11.13.18.05/purchaseOrders"},
                "sales_order": {"object": "Sales Order", "api": "salesOrders", "rest": "/fscmRestApi/resources/11.13.18.05/salesOrders"},
                "receipt": {"object": "Receipt", "api": "receipts", "rest": "/fscmRestApi/resources/11.13.18.05/receipts"},
                "invoice": {"object": "Payables Invoice", "api": "invoices", "rest": "/fscmRestApi/resources/11.13.18.05/invoices"},
                "item": {"object": "Inventory Item", "api": "inventoryItems", "rest": "/fscmRestApi/resources/11.13.18.05/inventoryItems"},
                "supplier": {"object": "Supplier", "api": "suppliers", "rest": "/fscmRestApi/resources/11.13.18.05/suppliers"},
            },
            "integration_protocols": ["REST (JSON)", "SOAP", "Oracle Integration Cloud (OIC)", "File-based Load"],
            "mcp_approach": "Use Oracle REST APIs with JWT auth; OIC pipelines for real-time sync",
        },
        "netsuite": {
            "name": "Oracle NetSuite",
            "modules": ["Order Management", "Inventory", "Procurement", "Financial Management",
                        "Warehouse Management", "Manufacturing"],
            "key_objects": {
                "purchase_order": {"object": "Purchase Order", "record_type": "purchaseorder", "rest": "/rest/record/v1/purchaseorder"},
                "sales_order": {"object": "Sales Order", "record_type": "salesorder", "rest": "/rest/record/v1/salesorder"},
                "item_receipt": {"object": "Item Receipt", "record_type": "itemreceipt", "rest": "/rest/record/v1/itemreceipt"},
                "vendor_bill": {"object": "Vendor Bill", "record_type": "vendorbill", "rest": "/rest/record/v1/vendorbill"},
                "inventory_item": {"object": "Inventory Item", "record_type": "inventoryitem", "rest": "/rest/record/v1/inventoryitem"},
                "vendor": {"object": "Vendor", "record_type": "vendor", "rest": "/rest/record/v1/vendor"},
            },
            "integration_protocols": ["SuiteQL (REST)", "SuiteTalk SOAP", "RESTlet", "CSV Import"],
            "mcp_approach": "Use SuiteQL for complex queries; REST Record API for CRUD; SuiteScript 2.x for custom logic",
        },
        "dynamics365": {
            "name": "Microsoft Dynamics 365 SCM",
            "modules": ["Supply Chain Management", "Finance", "Commerce", "Warehouse Management",
                        "Transportation Management", "Production Control"],
            "key_objects": {
                "purchase_order": {"object": "Purchase Order", "entity": "PurchaseOrderHeaders", "odata": "/data/PurchaseOrderHeaders"},
                "sales_order": {"object": "Sales Order", "entity": "SalesOrderHeadersV2", "odata": "/data/SalesOrderHeadersV2"},
                "product_receipt": {"object": "Product Receipt", "entity": "PurchaseOrderProductReceipts", "odata": "/data/PurchaseOrderProductReceipts"},
                "vendor_invoice": {"object": "Vendor Invoice", "entity": "VendorInvoiceHeaders", "odata": "/data/VendorInvoiceHeaders"},
                "released_product": {"object": "Released Product", "entity": "ReleasedProductsV2", "odata": "/data/ReleasedProductsV2"},
                "vendor": {"object": "Vendor", "entity": "VendorsV2", "odata": "/data/VendorsV2"},
            },
            "integration_protocols": ["OData (REST)", "SOAP", "Data Management Framework", "Logic Apps", "Azure Service Bus"],
            "mcp_approach": "Use D365 OData REST API; MCP server natively supported via Dynamics 365 ERP MCP (Build 2025)",
        },
    }

    ERP_FIELD_MAPPINGS = {
        "purchase_order": {
            "sap": {"id": "EKKO.EBELN", "vendor": "EKKO.LIFNR", "date": "EKKO.BEDAT", "amount": "EKKO.NETWR", "currency": "EKKO.WAERS", "status": "EKKO.STATU"},
            "oracle": {"id": "PO_NUMBER", "vendor": "SUPPLIER_ID", "date": "CREATION_DATE", "amount": "AMOUNT", "currency": "CURRENCY_CODE", "status": "STATUS"},
            "netsuite": {"id": "tranId", "vendor": "entity.id", "date": "tranDate", "amount": "total", "currency": "currency.id", "status": "status"},
            "dynamics365": {"id": "PurchaseOrderNumber", "vendor": "VendorAccountNumber", "date": "OrderDate", "amount": "TotalInvoiceAmount", "currency": "CurrencyCode", "status": "DocumentState"},
        },
        "sales_order": {
            "sap": {"id": "VBAK.VBELN", "customer": "VBAK.KUNNR", "date": "VBAK.AUDAT", "amount": "VBAK.NETWR", "currency": "VBAK.WAERS", "status": "VBAK.GBSTA"},
            "oracle": {"id": "ORDER_NUMBER", "customer": "CUSTOMER_ID", "date": "ORDERED_DATE", "amount": "ORDERED_AMOUNT", "currency": "TRANSACTIONAL_CURR_CODE", "status": "FLOW_STATUS_CODE"},
            "netsuite": {"id": "tranId", "customer": "entity.id", "date": "tranDate", "amount": "total", "currency": "currency.id", "status": "status"},
            "dynamics365": {"id": "SalesOrderNumber", "customer": "CustomerAccountNumber", "date": "RequestedShippingDate", "amount": "TotalAmount", "currency": "CurrencyCode", "status": "SalesOrderStatus"},
        },
        "invoice": {
            "sap": {"id": "RBKP.BELNR", "vendor": "RBKP.LIFNR", "date": "RBKP.BLDAT", "amount": "RBKP.RMWWR", "currency": "RBKP.WAERS", "status": "RBKP.RBSTAT"},
            "oracle": {"id": "INVOICE_NUM", "vendor": "VENDOR_ID", "date": "INVOICE_DATE", "amount": "INVOICE_AMOUNT", "currency": "INVOICE_CURRENCY_CODE", "status": "APPROVAL_STATUS"},
            "netsuite": {"id": "tranId", "vendor": "entity.id", "date": "tranDate", "amount": "total", "currency": "currency.id", "status": "status"},
            "dynamics365": {"id": "InvoiceNumber", "vendor": "VendorAccountNumber", "date": "InvoiceDate", "amount": "InvoiceAmount", "currency": "CurrencyCode", "status": "PaymentStatus"},
        },
    }

    # ---------------------------------------------------------------------------
    # Continuous Planning Templates
    # ---------------------------------------------------------------------------
    PLANNING_TEMPLATES = {
        "demand_sensing": {
            "title": "Demand Sensing & Forecasting Template",
            "horizon": "rolling_13_week",
            "inputs": [
                "Point-of-sale (POS) data feed",
                "E-commerce order velocity (last 7/14/28 days)",
                "Distributor sell-through rates",
                "Seasonal index by SKU/category",
                "Promotional calendar (promo lift factors)",
                "External signals: weather, events, economic indicators",
            ],
            "outputs": [
                "Statistical baseline forecast (ARIMA / ETS model)",
                "Consensus forecast with market intelligence overlay",
                "Forecast accuracy (MAPE, bias) by SKU tier",
                "Demand variability coefficient (CV) for safety stock calc",
            ],
            "review_cadence": "Weekly S&OP demand review",
            "mcp_context_fields": ["sku_id", "location_id", "week", "baseline_forecast",
                                   "adjusted_forecast", "actual_demand", "forecast_error", "promo_flag"],
        },
        "inventory_optimization": {
            "title": "Inventory Position & Optimization Template",
            "horizon": "rolling_26_week",
            "inputs": [
                "Current on-hand inventory by location",
                "In-transit inventory with ETA",
                "Open purchase orders and expected receipts",
                "Safety stock targets (service level driven)",
                "Reorder points and economic order quantities (EOQ)",
                "Inventory carrying cost rate",
            ],
            "outputs": [
                "Days of supply (DOS) by SKU/location",
                "Inventory health: overstock, healthy, understock, stockout risk",
                "Reorder recommendations with suggested quantities",
                "Working capital impact of reorder decisions",
            ],
            "review_cadence": "Daily inventory health review; weekly reorder execution",
            "mcp_context_fields": ["sku_id", "location_id", "on_hand_qty", "in_transit_qty",
                                   "open_po_qty", "safety_stock", "reorder_point", "dos",
                                   "inventory_status", "recommended_action"],
        },
        "constraint_management": {
            "title": "Supply Constraint & Capacity Template",
            "horizon": "rolling_12_week",
            "inputs": [
                "Supplier confirmed capacity by week",
                "Manufacturing capacity (hours / units) by line",
                "Transportation capacity by lane and mode",
                "DC/warehouse throughput constraints",
                "Known constraints: shutdowns, holidays, planned maintenance",
            ],
            "outputs": [
                "Constrained supply plan by SKU/week",
                "Constraint bottleneck identification (critical path)",
                "Allocation recommendations when supply < demand",
                "Recovery plan timeline for constraint resolution",
            ],
            "review_cadence": "Weekly supply review; real-time exception monitoring",
            "mcp_context_fields": ["sku_id", "supplier_id", "week", "unconstrained_plan",
                                   "constrained_plan", "constraint_type", "constraint_qty",
                                   "allocation_priority", "recovery_date"],
        },
        "sop_integration": {
            "title": "Sales & Operations Planning (S&OP) Integration Template",
            "horizon": "rolling_18_month",
            "inputs": [
                "Demand plan (consensus from demand sensing)",
                "Supply plan (constrained, from constraint management)",
                "Financial plan (revenue, margin, working capital targets)",
                "New product introduction (NPI) pipeline",
                "Strategic inventory build plans",
                "Customer service level commitments",
            ],
            "outputs": [
                "Integrated business plan: demand vs supply vs finance reconciliation",
                "Open issues and risks with recommended decisions",
                "Approved operational plan for execution",
                "KPI dashboard: fill rate, inventory turns, OTD, forecast accuracy",
            ],
            "review_cadence": "Monthly executive S&OP; weekly operational review",
            "mcp_context_fields": ["month", "product_family", "demand_plan", "supply_plan",
                                   "financial_target", "gap_to_plan", "risk_flag",
                                   "decision_required", "approved_plan"],
        },
    }

    # ---------------------------------------------------------------------------
    # Carbon Footprint & Sustainability Data
    # ---------------------------------------------------------------------------
    CARBON_EMISSION_FACTORS = {
        "transport_modes": {
            "air_freight": {
                "kg_co2e_per_tonne_km": 0.602,
                "description": "Air freight (average belly + freighter)",
                "relative_impact": "highest",
                "use_cases": "Time-critical, high-value, low-weight goods",
            },
            "ocean_freight_container": {
                "kg_co2e_per_tonne_km": 0.016,
                "description": "Container shipping (average VLCC to feeder)",
                "relative_impact": "lowest_for_long_distance",
                "use_cases": "Bulk transcontinental trade, non-time-sensitive",
            },
            "road_truck_diesel": {
                "kg_co2e_per_tonne_km": 0.096,
                "description": "Diesel truck (average 40t GVW, 50% load)",
                "relative_impact": "medium",
                "use_cases": "Regional distribution, last-mile",
            },
            "road_truck_electric": {
                "kg_co2e_per_tonne_km": 0.028,
                "description": "Battery-electric truck (EU grid average)",
                "relative_impact": "low",
                "use_cases": "Urban last-mile, short-haul distribution",
            },
            "rail_freight": {
                "kg_co2e_per_tonne_km": 0.028,
                "description": "Rail freight (average diesel + electric mix)",
                "relative_impact": "low",
                "use_cases": "Long-haul continental, intermodal with road",
            },
            "intermodal_rail_road": {
                "kg_co2e_per_tonne_km": 0.042,
                "description": "Intermodal (rail + road drayage)",
                "relative_impact": "low_to_medium",
                "use_cases": "Continental trade lanes, port to inland DC",
            },
        },
        "scope3_categories": {
            "cat_1_purchased_goods": {
                "description": "Upstream emissions from purchased goods and services",
                "calculation_method": "Spend-based or activity-based (kg CO2e per $ spend or per unit)",
                "data_needed": ["Supplier Scope 1+2 emissions", "Spend by category", "Emission intensity factors"],
            },
            "cat_4_upstream_transport": {
                "description": "Transportation of purchased goods to your facility",
                "calculation_method": "Tonne-km × emission factor per transport mode",
                "data_needed": ["Shipment weight (tonnes)", "Distance (km)", "Transport mode"],
            },
            "cat_9_downstream_transport": {
                "description": "Transportation of sold goods to customer",
                "calculation_method": "Tonne-km × emission factor per transport mode",
                "data_needed": ["Shipment weight (tonnes)", "Distance (km)", "Transport mode"],
            },
            "cat_11_use_of_sold_products": {
                "description": "Emissions from customer use of sold products",
                "calculation_method": "Lifetime energy consumption × grid emission factor",
                "data_needed": ["Product energy consumption profile", "Customer location grid factor"],
            },
        },
        "routing_optimization": {
            "carbon_score_formula": "base_emissions × (1 - load_factor_bonus) × route_efficiency_factor",
            "carbon_vs_cost_tradeoffs": [
                "Air → Rail shift: ~94% emission reduction, +3-5 days transit",
                "Road → Rail shift: ~70% emission reduction, +1-2 days transit",
                "Consolidation (LTL → FTL): ~30-50% emission reduction per unit, volume dependent",
                "Nearshoring: reduces Cat 4 transport emissions, may increase Cat 1 production emissions",
                "Modal shift to ocean: ~80% emission reduction vs air, +2-4 weeks transit",
            ],
            "green_corridors": [
                "Rotterdam → Antwerp → Duisburg (Rhine corridor, electrified rail)",
                "Los Angeles → Chicago (rail intermodal, fastest in US)",
                "Singapore → Busan (container shipping, highest efficiency lane)",
                "Mexico City → Laredo → Dallas (nearshore road corridor)",
            ],
        },
    }

    def __init__(self):
        self.server = Server("cis-assistant")
        self.contracts: Dict[str, Any] = {}
        self.error_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.examples: List[Dict[str, Any]] = []
        self.bible_content: str = self._load_bible_content()
        # Continuous planning sessions (in-memory rolling context)
        self.planning_sessions: Dict[str, Dict[str, Any]] = {}

        # Register handlers
        self._setup_handlers()
    
    def _is_safe_bible_path(self, path: Path, allowed_roots: List[Path]) -> bool:
        """
        Validate that the requested Bible path is within one of the allowed roots.
        This prevents the CIS_BIBLE_PATH environment variable from pointing to
        arbitrary locations on the filesystem.
        """
        try:
            resolved_path = path.expanduser().resolve()
        except Exception:
            # If resolution fails (e.g., due to symlink issues), treat as unsafe.
            return False

        for root in allowed_roots:
            try:
                # Will raise ValueError if resolved_path is not within root.
                resolved_path.relative_to(root)
                return True
            except ValueError:
                continue
        return False

    def _load_bible_content(self) -> str:
        """Load the Circulatory Informatics Bible content"""
        # Try to find the Bible file relative to the package or from environment
        base_file_path = Path(__file__).resolve()
        allowed_roots: List[Path] = [
            base_file_path.parents[3],
            base_file_path.parents[2],
            Path.cwd().resolve(),
        ]

        bible_env_path = os.environ.get("CIS_BIBLE_PATH")
        
        possible_paths: List[Path] = []
        if bible_env_path:
            env_candidate = Path(bible_env_path)
            if self._is_safe_bible_path(env_candidate, allowed_roots):
                possible_paths.append(env_candidate)
        
        possible_paths.extend([
            base_file_path.parents[3] / "Bible",
            base_file_path.parents[2] / "Bible",
            Path.cwd().resolve() / "Bible",
        ])
        
        for bible_path in possible_paths:
            if bible_path.is_file():
                try:
                    with open(bible_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except (OSError, UnicodeDecodeError):
                    # Continue to try other paths if this one fails
                    continue
        
        return ""
    
    def _extract_bible_section(self, section_name: str) -> str:
        """Extract a specific section from the Bible content"""
        if not self.bible_content:
            return "Bible content not available."
        
        # Define section markers and their content ranges
        sections = {
            "philosophy": ("PART I: PHILOSOPHICAL FOUNDATIONS", "PART II: SCIENTIFIC"),
            "seven_principles": ("2.1 The Seven Principles", "2.2 The Circulatory Metaphor"),
            "nine_systems": ("5. The Nine Systems", "PART III:"),
            "vibe_coding": ("3. How Living Code Achieves", "PART II:"),
            "scientific_foundations": ("PART II: SCIENTIFIC FOUNDATIONS", "PART III:"),
        }
        
        if section_name.lower() not in sections:
            return f"Section '{section_name}' not found. Available: {', '.join(sections.keys())}"
        
        start_marker, end_marker = sections[section_name.lower()]
        
        start_idx = self.bible_content.find(start_marker)
        end_idx = self.bible_content.find(end_marker, start_idx + len(start_marker))
        
        if start_idx == -1:
            return f"Section '{section_name}' not found in Bible content."
        
        if end_idx == -1:
            return self._truncate_bible_section(self.bible_content[start_idx:])
        
        return self._truncate_bible_section(self.bible_content[start_idx:end_idx])

    def _truncate_bible_section(self, text: str) -> str:
        """
        Truncate Bible section text to MAX_BIBLE_SECTION_LENGTH, preferring
        sentence/paragraph boundaries and indicating when content is truncated.
        """
        # If no limit is defined for some reason, or text is already short enough,
        # return the text unchanged.
        max_len = getattr(self, "MAX_BIBLE_SECTION_LENGTH", None)
        if max_len is None or len(text) <= max_len:
            return text
        
        # Reserve space for ellipsis when truncating.
        ellipsis = "..."
        if max_len <= len(ellipsis):
            # Degenerate case: not enough room for ellipsis and content.
            return text[:max_len]
        
        # Work with a base slice within the maximum length.
        base = text[:max_len]
        
        # Try to find a natural boundary (paragraph or sentence end) within base.
        boundary_indices: list[int] = []
        
        # Prefer paragraph boundaries first.
        for marker in ["\n\n", "\n"]:
            idx = base.rfind(marker)
            if idx != -1:
                # Cut at the end of the marker.
                boundary_indices.append(idx + len(marker))
                break
        
        # If no paragraph boundary found, look for sentence endings.
        if not boundary_indices:
            for marker in [". ", "? ", "! "]:
                idx = base.rfind(marker)
                if idx != -1:
                    boundary_indices.append(idx + len(marker))
                    break
        
        if boundary_indices:
            cut_pos = boundary_indices[0]
            candidate = base[:cut_pos].rstrip()
        else:
            # Fall back to a hard cut just before the ellipsis space.
            candidate = base[: max_len - len(ellipsis)].rstrip()
        
        # Ensure final result (candidate + ellipsis) does not exceed max_len.
        if len(candidate) + len(ellipsis) > max_len:
            candidate = candidate[: max_len - len(ellipsis)]
        
        return candidate + ellipsis
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available CIS Assistant tools"""
            return [
                Tool(
                    name="generate_contract",
                    description="Generate a contract specification for a software component",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "component_name": {
                                "type": "string",
                                "description": "Name of the component to generate a contract for"
                            },
                            "component_type": {
                                "type": "string",
                                "description": "Type of component (e.g., 'class', 'function', 'module')",
                                "enum": ["class", "function", "module", "service", "api"]
                            },
                            "requirements": {
                                "type": "object",
                                "description": "Requirements and constraints for the component"
                            }
                        },
                        "required": ["component_name", "component_type", "requirements"]
                    }
                ),
                Tool(
                    name="validate_implementation",
                    description="Validate code implementation against a contract",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "contract_id": {
                                "type": "string",
                                "description": "ID of the contract to validate against"
                            },
                            "code": {
                                "type": "string",
                                "description": "Code to validate"
                            }
                        },
                        "required": ["contract_id", "code"]
                    }
                ),
                Tool(
                    name="record_error_pattern",
                    description="Record an error pattern for future learning",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "error_type": {
                                "type": "string",
                                "description": "Type of error encountered"
                            },
                            "code_before": {
                                "type": "string",
                                "description": "Code before fix"
                            },
                            "code_after": {
                                "type": "string",
                                "description": "Code after fix"
                            },
                            "context": {
                                "type": "object",
                                "description": "Context information about the error"
                            }
                        },
                        "required": ["error_type", "code_before", "code_after"]
                    }
                ),
                Tool(
                    name="get_fix_suggestions",
                    description="Get fix suggestions based on historical error patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "error_type": {
                                "type": "string",
                                "description": "Type of error to get suggestions for"
                            },
                            "current_code": {
                                "type": "string",
                                "description": "Current code with error"
                            }
                        },
                        "required": ["error_type", "current_code"]
                    }
                ),
                Tool(
                    name="add_example",
                    description="Add a code example to the example library",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "example_type": {
                                "type": "string",
                                "description": "Type of example (e.g., 'pattern', 'implementation', 'test')"
                            },
                            "code": {
                                "type": "string",
                                "description": "Example code"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the example"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for categorization"
                            }
                        },
                        "required": ["example_type", "code", "description"]
                    }
                ),
                Tool(
                    name="search_examples",
                    description="Search the example library",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "example_type": {
                                "type": "string",
                                "description": "Optional filter by example type"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional filter by tags"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="list_contracts",
                    description="List all generated contracts",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_contract",
                    description="Get details of a specific contract",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "contract_id": {
                                "type": "string",
                                "description": "ID of the contract to retrieve"
                            }
                        },
                        "required": ["contract_id"]
                    }
                ),
                Tool(
                    name="get_cis_principles",
                    description="Get CIS (Circulatory Informatics System) principles and methodology guidelines for maintaining adherence to circulatory informatics structure",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "principle": {
                                "type": "string",
                                "description": "Specific principle to retrieve (optional). Options: distributed_autonomy, continuous_sensing, feedback_driven_adaptation, emergent_intelligence, memory_and_learning, graceful_degradation, efficient_resource_flow",
                                "enum": ["distributed_autonomy", "continuous_sensing", "feedback_driven_adaptation", "emergent_intelligence", "memory_and_learning", "graceful_degradation", "efficient_resource_flow"]
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_llm_coding_aid",
                    description="Get guidance for common LLM coding issues and their solutions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_type": {
                                "type": "string",
                                "description": "Type of LLM coding issue. Options: context_window_overflow, hallucinated_imports, inconsistent_naming, missing_error_handling, type_hint_inconsistency, incomplete_implementation, security_vulnerabilities, logic_drift",
                                "enum": ["context_window_overflow", "hallucinated_imports", "inconsistent_naming", "missing_error_handling", "type_hint_inconsistency", "incomplete_implementation", "security_vulnerabilities", "logic_drift"]
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_bible_section",
                    description="Get a section from the Circulatory Informatics Bible for methodology reference and adherence guidance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "section": {
                                "type": "string",
                                "description": "Section to retrieve. Options: philosophy, seven_principles, nine_systems, vibe_coding, scientific_foundations",
                                "enum": ["philosophy", "seven_principles", "nine_systems", "vibe_coding", "scientific_foundations"]
                            }
                        },
                        "required": ["section"]
                    }
                ),
                Tool(
                    name="check_cis_compliance",
                    description="Check if code or design adheres to CIS principles and get recommendations for improvement",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to check for CIS compliance"
                            },
                            "component_description": {
                                "type": "string",
                                "description": "Description of what the component does"
                            }
                        },
                        "required": ["code", "component_description"]
                    }
                ),
                Tool(
                    name="get_base_network_info",
                    description="Get Base L2 network configuration, endpoints, and details for blockchain development on the Base platform",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "network": {
                                "type": "string",
                                "description": "Network to get info for: mainnet or sepolia (testnet)",
                                "enum": ["mainnet", "sepolia"]
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="generate_supply_chain_contract",
                    description="Generate a Solidity smart contract template for supply chain use cases on Base L2, including product tracking, supplier registry, invoice management, and certification NFTs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template_type": {
                                "type": "string",
                                "description": "Type of supply chain contract to generate",
                                "enum": ["product_tracking", "supplier_registry", "invoice_management", "certification_nft"]
                            },
                            "business_name": {
                                "type": "string",
                                "description": "Optional name of the business for reference; not automatically injected into the generated contract source"
                            }
                        },
                        "required": ["template_type"]
                    }
                ),
                Tool(
                    name="get_supply_chain_templates",
                    description="List all available supply chain smart contract templates with descriptions and use cases for Base L2 blockchain",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_business_onboarding_guide",
                    description="Get step-by-step guidance for small businesses to adopt blockchain technology on Base L2 for supply chain management",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "guide_section": {
                                "type": "string",
                                "description": "Section of the onboarding guide to retrieve",
                                "enum": ["getting_started", "cost_analysis", "use_case_guide", "integration_guide"]
                            },
                            "business_type": {
                                "type": "string",
                                "description": "Optional business type for tailored recommendations: retail, food_beverage, manufacturing, services, wholesale_distribution",
                                "enum": ["retail", "food_beverage", "manufacturing", "services", "wholesale_distribution"]
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="validate_smart_contract",
                    description="Validate Solidity smart contract code for common issues, security patterns, and Base L2 compatibility",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Solidity smart contract code to validate"
                            },
                            "contract_type": {
                                "type": "string",
                                "description": "Optional type of contract for context-aware validation",
                                "enum": ["product_tracking", "supplier_registry", "invoice_management", "certification_nft", "custom"]
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_supplier_intelligence",
                    description="Assess supplier risk across financial health, geopolitical exposure, lead time variance, and ESG scores. Returns a structured risk report with signals, risk levels, and recommended data sources.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "risk_category": {
                                "type": "string",
                                "description": "Risk category to assess. Omit to get all categories.",
                                "enum": ["financial_health", "geopolitical_exposure", "lead_time_variance", "esg_scores"]
                            },
                            "supplier_name": {
                                "type": "string",
                                "description": "Optional supplier name for context (used in report labeling)"
                            },
                            "industry": {
                                "type": "string",
                                "description": "Optional industry vertical for tailored guidance (e.g., electronics, food, apparel)"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="normalize_carrier_tracking",
                    description="Get normalized carrier tracking schemas and API integration guidance for FedEx, UPS, Maersk, and DHL. Returns a unified multi-modal visibility layer definition.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "carrier": {
                                "type": "string",
                                "description": "Specific carrier to retrieve API details for. Omit to get the normalized schema and all carriers.",
                                "enum": ["fedex", "ups", "maersk", "dhl"]
                            },
                            "use_case": {
                                "type": "string",
                                "description": "Integration use case for tailored guidance",
                                "enum": ["tracking_visibility", "rate_shopping", "shipment_booking", "webhook_events"]
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="bridge_erp_context",
                    description="Translate data objects and field mappings between ERP systems (SAP, Oracle Fusion, NetSuite, Dynamics 365). Returns field-level mapping and integration protocol guidance for the cross-ERP context bridge.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_erp": {
                                "type": "string",
                                "description": "Source ERP system",
                                "enum": ["sap", "oracle", "netsuite", "dynamics365"]
                            },
                            "target_erp": {
                                "type": "string",
                                "description": "Target ERP system",
                                "enum": ["sap", "oracle", "netsuite", "dynamics365"]
                            },
                            "data_category": {
                                "type": "string",
                                "description": "Data category to map between systems",
                                "enum": ["purchase_order", "sales_order", "invoice", "all"]
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_continuous_planning_template",
                    description="Get a continuous planning template with rolling demand signals, inventory positions, and constraint history. Supports persistent planning partner workflows across demand sensing, inventory optimization, constraint management, and S&OP.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "planning_type": {
                                "type": "string",
                                "description": "Type of planning template to retrieve. Omit to list all available templates.",
                                "enum": ["demand_sensing", "inventory_optimization", "constraint_management", "sop_integration"]
                            },
                            "session_id": {
                                "type": "string",
                                "description": "Optional session ID to retrieve or continue a named planning session"
                            },
                            "context_update": {
                                "type": "object",
                                "description": "Optional key-value pairs to update/record in the planning session context (e.g., current demand figures, constraint changes)"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="assess_supply_chain_carbon",
                    description="Calculate Scope 3 carbon footprint for supply chain operations and get carbon-aware routing recommendations. Injects CO2e data into planning and logistics decisions.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "transport_mode": {
                                "type": "string",
                                "description": "Transport mode to assess or compare",
                                "enum": ["air_freight", "ocean_freight_container", "road_truck_diesel", "road_truck_electric", "rail_freight", "intermodal_rail_road"]
                            },
                            "weight_tonnes": {
                                "type": "number",
                                "description": "Shipment weight in metric tonnes"
                            },
                            "distance_km": {
                                "type": "number",
                                "description": "Transport distance in kilometres"
                            },
                            "scope3_category": {
                                "type": "string",
                                "description": "Scope 3 category to analyse. Omit to get all categories.",
                                "enum": ["cat_1_purchased_goods", "cat_4_upstream_transport", "cat_9_downstream_transport", "cat_11_use_of_sold_products"]
                            },
                            "compare_modes": {
                                "type": "boolean",
                                "description": "If true, returns a comparison of all transport modes for the given weight and distance"
                            }
                        },
                        "required": []
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            
            if name == "generate_contract":
                return await self._generate_contract(arguments)
            elif name == "validate_implementation":
                return await self._validate_implementation(arguments)
            elif name == "record_error_pattern":
                return await self._record_error_pattern(arguments)
            elif name == "get_fix_suggestions":
                return await self._get_fix_suggestions(arguments)
            elif name == "add_example":
                return await self._add_example(arguments)
            elif name == "search_examples":
                return await self._search_examples(arguments)
            elif name == "list_contracts":
                return await self._list_contracts(arguments)
            elif name == "get_contract":
                return await self._get_contract(arguments)
            elif name == "get_cis_principles":
                return await self._get_cis_principles(arguments)
            elif name == "get_llm_coding_aid":
                return await self._get_llm_coding_aid(arguments)
            elif name == "get_bible_section":
                return await self._get_bible_section(arguments)
            elif name == "check_cis_compliance":
                return await self._check_cis_compliance(arguments)
            elif name == "get_base_network_info":
                return await self._get_base_network_info(arguments)
            elif name == "generate_supply_chain_contract":
                return await self._generate_supply_chain_contract(arguments)
            elif name == "get_supply_chain_templates":
                return await self._get_supply_chain_templates(arguments)
            elif name == "get_business_onboarding_guide":
                return await self._get_business_onboarding_guide(arguments)
            elif name == "validate_smart_contract":
                return await self._validate_smart_contract(arguments)
            elif name == "get_supplier_intelligence":
                return await self._get_supplier_intelligence(arguments)
            elif name == "normalize_carrier_tracking":
                return await self._normalize_carrier_tracking(arguments)
            elif name == "bridge_erp_context":
                return await self._bridge_erp_context(arguments)
            elif name == "get_continuous_planning_template":
                return await self._get_continuous_planning_template(arguments)
            elif name == "assess_supply_chain_carbon":
                return await self._assess_supply_chain_carbon(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        @self.server.list_prompts()
        async def list_prompts() -> list[Prompt]:
            """List available prompts"""
            return [
                Prompt(
                    name="contract_first_development",
                    description="Guide for contract-first development workflow",
                    arguments=[
                        PromptArgument(
                            name="component_type",
                            description="Type of component to develop",
                            required=True
                        )
                    ]
                ),
                Prompt(
                    name="debug_validation_error",
                    description="Guide for debugging validation errors",
                    arguments=[
                        PromptArgument(
                            name="error_message",
                            description="The validation error message",
                            required=True
                        )
                    ]
                ),
                Prompt(
                    name="cis_methodology_guide",
                    description="Guide for implementing code following Circulatory Informatics System principles",
                    arguments=[
                        PromptArgument(
                            name="focus_area",
                            description="Area to focus on: architecture, error_handling, observability, resilience",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="llm_coding_best_practices",
                    description="Best practices for LLM-assisted code generation to avoid common issues",
                    arguments=[]
                ),
                Prompt(
                    name="blockchain_supply_chain_setup",
                    description="Step-by-step workflow for setting up supply chain tracking on Base L2 blockchain",
                    arguments=[
                        PromptArgument(
                            name="business_type",
                            description="Type of business: retail, food_beverage, manufacturing, services, wholesale_distribution",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="small_business_onboarding",
                    description="Complete guide for small businesses to adopt blockchain technology on Base L2 for supply chain and business operations",
                    arguments=[
                        PromptArgument(
                            name="focus_area",
                            description="Area to focus on: getting_started, cost_analysis, integration, all",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="supplier_intelligence_workflow",
                    description="Step-by-step guide for building a supplier risk intelligence process covering financial health, geopolitical exposure, lead time variance, and ESG scoring",
                    arguments=[
                        PromptArgument(
                            name="risk_category",
                            description="Risk category to focus on: financial_health, geopolitical_exposure, lead_time_variance, esg_scores, all",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="sustainability_planning_guide",
                    description="Guide for embedding Scope 3 carbon data into supply chain planning and logistics decisions for carbon-aware routing and sourcing",
                    arguments=[
                        PromptArgument(
                            name="focus_area",
                            description="Area to focus on: carbon_calculation, modal_shift, scope3_reporting, green_routing",
                            required=False
                        )
                    ]
                ),
            ]

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
            """Get a specific prompt"""
            if name == "contract_first_development":
                component_type = arguments.get("component_type", "component") if arguments else "component"
                return GetPromptResult(
                    description=f"Contract-first development workflow for {component_type}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""# Contract-First Development Workflow for {component_type}

## Step 1: Generate Contract
Use the `generate_contract` tool to create a formal specification:
- Define clear input/output interfaces
- Specify constraints and validation rules
- Document expected behavior

## Step 2: Review Contract
Ensure the contract captures all requirements:
- Check completeness of interface definitions
- Verify constraints are explicit
- Confirm validation criteria are clear

## Step 3: Implement Code
Write code that satisfies the contract:
- Follow the interface specification
- Respect all constraints
- Handle edge cases

## Step 4: Validate Implementation
Use `validate_implementation` tool to check compliance:
- Verify interface conformance
- Check constraint satisfaction
- Review validation results

## Step 5: Iterate if Needed
If validation fails:
- Use `get_fix_suggestions` for guidance
- Record successful fixes with `record_error_pattern`
- Re-validate until all checks pass

This workflow ensures high-quality, maintainable code by establishing clear contracts before implementation."""
                            )
                        )
                    ]
                )
            elif name == "debug_validation_error":
                error_message = arguments.get("error_message", "") if arguments else ""
                return GetPromptResult(
                    description="Guide for debugging validation errors",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""# Debugging Validation Error

## Error Message
{error_message}

## Debugging Steps

1. **Understand the Error**
   - Read the error message carefully
   - Identify the specific contract violation
   - Locate the problematic code section

2. **Search for Similar Patterns**
   Use `get_fix_suggestions` with the error type to find:
   - Historical fixes for similar errors
   - Common patterns and solutions
   - Context-specific guidance

3. **Apply the Fix**
   - Make minimal changes to address the error
   - Maintain code consistency
   - Preserve all other constraints

4. **Re-validate**
   - Use `validate_implementation` again
   - Ensure the fix doesn't introduce new errors
   - Verify all constraints are satisfied

5. **Record Success**
   Once fixed, use `record_error_pattern` to:
   - Document the fix for future reference
   - Help others with similar issues
   - Improve the system's learning

## Tips
- Start with the most specific error first
- Check for type mismatches and missing imports
- Verify all required methods/properties are present
- Ensure naming conventions are followed"""
                            )
                        )
                    ]
                )
            elif name == "cis_methodology_guide":
                focus_area = arguments.get("focus_area", "general") if arguments else "general"
                return GetPromptResult(
                    description="Circulatory Informatics System methodology guide",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""# Circulatory Informatics System (CIS) Methodology Guide

## Focus Area: {focus_area.replace('_', ' ').title()}

## The Seven Principles of Living Code

### 1. Distributed Autonomy
**Principle:** No single point of control. Each 'organ' operates autonomously within a decentralized governance framework.
**Code Pattern:** Decouple components, use message queues, avoid synchronous dependencies.

### 2. Continuous Sensing
**Principle:** The organism must continuously monitor its own state through events.
**Code Pattern:** Add logging, metrics, and health checks to all components.

### 3. Feedback-Driven Adaptation
**Principle:** Adaptation requires feedback loops that measure deviation and trigger corrective action.
**Code Pattern:** Implement retry logic, circuit breakers, and automatic recovery mechanisms.

### 4. Emergent Intelligence
**Principle:** Intelligence emerges from interaction of simple agents following local rules.
**Code Pattern:** Design small, focused components that communicate through well-defined interfaces.

### 5. Memory and Learning
**Principle:** The organism learns from past events and adjusts future behavior.
**Code Pattern:** Record error patterns, track successful fixes, build adaptive example libraries.

### 6. Graceful Degradation
**Principle:** No single component is essential. The system continues functioning when components fail.
**Code Pattern:** Use fallbacks, timeouts, and isolation patterns to prevent cascading failures.

### 7. Efficient Resource Flow
**Principle:** Resources flow to where they're needed. Demand drives allocation.
**Code Pattern:** Implement resource pooling, lazy loading, and demand-based scaling.

## Implementation Checklist

When developing a component, ensure it follows these CIS principles:

- [ ] Component can operate independently (Distributed Autonomy)
- [ ] Component emits events/logs for monitoring (Continuous Sensing)
- [ ] Component handles failures and retries (Feedback-Driven Adaptation)
- [ ] Component has single responsibility (Emergent Intelligence)
- [ ] Component learns from errors (Memory and Learning)
- [ ] Component fails gracefully (Graceful Degradation)
- [ ] Component scales with demand (Efficient Resource Flow)

## Tools Available

Use these CIS Assistant tools to maintain methodology adherence:
- `get_cis_principles` - Get detailed principle guidance
- `check_cis_compliance` - Validate code against CIS principles
- `get_bible_section` - Access Circulatory Informatics Bible sections
- `get_llm_coding_aid` - Get help with common LLM coding issues"""
                            )
                        )
                    ]
                )
            elif name == "llm_coding_best_practices":
                return GetPromptResult(
                    description="Best practices for LLM-assisted code generation",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text="""# LLM-Assisted Code Generation Best Practices

## Common Issues and Solutions

### 1. Context Window Overflow
**Problem:** LLM loses context with large codebases
**Solutions:**
- Break code into smaller, focused modules
- Use progressive context loading
- Summarize distant context before providing detail

### 2. Hallucinated Imports
**Problem:** LLM invents non-existent libraries or APIs
**Solutions:**
- Always verify imports exist before using them
- Provide explicit list of available dependencies
- Include actual import statements from working code

### 3. Inconsistent Naming
**Problem:** LLM uses inconsistent naming conventions
**Solutions:**
- Provide explicit naming convention rules upfront
- Include examples of correct naming in context
- Use constraint checklists that specify naming patterns

### 4. Missing Error Handling
**Problem:** LLM omits try/except blocks and edge case handling
**Solutions:**
- Explicitly require error handling in contracts
- Provide examples with comprehensive error handling
- Add validation rules that check for exception handling

### 5. Type Hint Inconsistency
**Problem:** LLM provides incomplete or incorrect type hints
**Solutions:**
- Enforce type hints through validation rules
- Provide type hint examples for complex types
- Validate with mypy or similar tools

### 6. Incomplete Implementation
**Problem:** LLM provides stub implementations or 'pass' statements
**Solutions:**
- Require complete implementations in constraints
- Validate that no 'pass' or 'TODO' remains
- Use progressive example complexity

### 7. Security Vulnerabilities
**Problem:** LLM generates code with common security issues
**Solutions:**
- Include security constraints in contracts
- Validate input sanitization
- Check for hardcoded secrets patterns

### 8. Logic Drift
**Problem:** LLM solution drifts from original intent over iterations
**Solutions:**
- Maintain explicit contract reference throughout
- Use checkpoints to preserve known-good states
- Re-state original requirements when iterating

## Tools Available

Use `get_llm_coding_aid` with a specific issue type for detailed guidance on any of these issues."""
                            )
                        )
                    ]
                )
            elif name == "blockchain_supply_chain_setup":
                business_type = arguments.get("business_type", "general") if arguments else "general"
                return GetPromptResult(
                    description=f"Blockchain supply chain setup workflow for {business_type} business",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""# Blockchain Supply Chain Setup on Base L2

## Business Type: {business_type.replace('_', ' ').title()}

## Step 1: Choose Your Network
Start with **Base Sepolia testnet** for development and testing.
Use `get_base_network_info` to get network configuration details.

- Testnet: Chain ID 84532, RPC: https://sepolia.base.org
- Mainnet: Chain ID 8453, RPC: https://mainnet.base.org

## Step 2: Select Supply Chain Contracts
Use `get_supply_chain_templates` to browse available contract templates:
- **Product Tracking**: Track goods through supply chain stages
- **Supplier Registry**: Build a verified supplier network
- **Invoice Management**: On-chain B2B payment tracking
- **Certification NFT**: Issue verifiable certifications

## Step 3: Generate Your Smart Contract
Use `generate_supply_chain_contract` to create a customized contract:
- Select the template that matches your use case
- Review the generated Solidity code
- Customize fields and logic for your business needs

## Step 4: Validate Your Contract
Use `validate_smart_contract` to check for:
- Security best practices
- Gas optimization opportunities
- Base L2 compatibility
- Common vulnerability patterns

## Step 5: Deploy to Testnet
1. Set up a development environment (Hardhat or Foundry recommended)
2. Configure for Base Sepolia testnet
3. Deploy and test all contract functions
4. Verify contract on BaseScan

## Step 6: Integration
Use `get_business_onboarding_guide(guide_section="integration_guide")` for:
- Connecting to existing business systems
- Setting up event listeners
- Building user interfaces

## Step 7: Go Live on Base Mainnet
1. Complete testing on Sepolia
2. Audit smart contract code
3. Deploy to Base mainnet
4. Monitor transactions on BaseScan

## Available Tools
- `get_base_network_info` - Network configuration
- `generate_supply_chain_contract` - Contract generation
- `get_supply_chain_templates` - Browse templates
- `validate_smart_contract` - Contract validation
- `get_business_onboarding_guide` - Business adoption guides
- `check_cis_compliance` - CIS methodology compliance"""
                            )
                        )
                    ]
                )
            elif name == "small_business_onboarding":
                focus_area = arguments.get("focus_area", "all") if arguments else "all"
                return GetPromptResult(
                    description=f"Small business blockchain onboarding guide - {focus_area}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""# Small Business Blockchain Onboarding Guide

## Focus: {focus_area.replace('_', ' ').title()}

## Why Base L2 for Small Businesses?

Base is an Ethereum Layer 2 network that makes blockchain accessible and affordable:
- **Ultra-low costs**: Transactions cost less than $0.01
- **Fast confirmations**: ~2 second block times
- **Ethereum security**: Secured by Ethereum's network
- **Growing ecosystem**: Access to DeFi, NFTs, and business tools
- **No platform fees**: Pay only for transactions you make

## Getting Started

### 1. Set Up Your Business Wallet
- Install MetaMask or Coinbase Wallet
- Create a dedicated business wallet
- Secure your seed phrase safely
- Add Base network to your wallet

### 2. Understand the Costs
Use `get_business_onboarding_guide(guide_section="cost_analysis")` to see:
- Per-transaction costs (< $0.01)
- Contract deployment costs ($0.10-$1.00)
- Monthly operating estimates ($5-$50)
- Comparison with traditional software ($200-$2000/month)

### 3. Choose Your Use Case
Use `get_business_onboarding_guide(guide_section="use_case_guide")` to find the right fit:
- **Retail**: Inventory tracking, product authenticity
- **Food & Beverage**: Farm-to-table traceability, certifications
- **Manufacturing**: Parts tracking, quality control
- **Services**: Invoice management, credential verification
- **Wholesale/Distribution**: Shipment tracking, B2B payments

### 4. Deploy Your First Contract
Use `generate_supply_chain_contract` to create a smart contract:
- Start with the template that matches your needs
- Test on Base Sepolia testnet first
- Deploy to mainnet when ready

### 5. Integrate with Your Business
Use `get_business_onboarding_guide(guide_section="integration_guide")` for:
- Connecting blockchain to your existing systems
- Recommended development tools
- Staff training resources

## Key Benefits for Small Businesses

1. **Transparency**: Every transaction is verifiable and permanent
2. **Trust**: Build reputation through on-chain track record
3. **Efficiency**: Automate payments, certifications, and tracking
4. **Access**: Connect with global supply chains and marketplaces
5. **Cost Savings**: Eliminate intermediary fees and reduce paperwork
6. **Growth**: Access new markets and business opportunities

## Available Tools

- `get_base_network_info` - Learn about Base L2 network
- `get_supply_chain_templates` - Browse available contract templates
- `generate_supply_chain_contract` - Generate customized contracts
- `validate_smart_contract` - Validate contract security
- `get_business_onboarding_guide` - Detailed adoption guides
- `get_cis_principles` - CIS methodology for robust design"""
                            )
                        )
                    ]
                )
            elif name == "supplier_intelligence_workflow":
                risk_category = arguments.get("risk_category", "all") if arguments else "all"
                return GetPromptResult(
                    description=f"Supplier risk intelligence workflow - {risk_category}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""# Supplier Intelligence Workflow

## Focus: {risk_category.replace('_', ' ').title()}

## Why Supplier Intelligence Matters

Supplier disruptions account for over 40% of supply chain failures. A continuous supplier
intelligence process surfaces risks before they become disruptions.

## The Four Risk Dimensions

### 1. Financial Health
Monitor credit ratings, cash flow trends, and revenue concentration.
Use `get_supplier_intelligence(risk_category="financial_health")` to see signals and risk levels.

### 2. Geopolitical Exposure
Track country risk, sanctions, tariffs, and FX volatility.
Use `get_supplier_intelligence(risk_category="geopolitical_exposure")` for country risk factors.

### 3. Lead Time Variance
Watch OTD%, lead time mean/stdev, and port congestion.
Use `get_supplier_intelligence(risk_category="lead_time_variance")` for delivery performance signals.

### 4. ESG Scores
Assess carbon emissions intensity, labor standards, and third-party audit results.
Use `get_supplier_intelligence(risk_category="esg_scores")` for ESG scoring framework.

## Building Your Supplier Risk Register

1. **Tier your suppliers**: Critical (single source), Important (dual source), Standard (multi source)
2. **Assign risk categories**: Run `get_supplier_intelligence` for each category across Tier 1 suppliers
3. **Set monitoring cadence**: Weekly for critical, monthly for important, quarterly for standard
4. **Define escalation thresholds**: Risk level changes trigger procurement or engineering review
5. **Connect to planning**: Feed risk signals into `get_continuous_planning_template` for constrained supply plans

## Data Source Integration

- EcoVadis / CDP for ESG → feed into `esg_scores` risk category
- Everstream Analytics / Riskmethods for geopolitical → `geopolitical_exposure`
- ERP OTD data → `lead_time_variance` (use `bridge_erp_context` to normalize across ERPs)
- D&B / Coface for financial → `financial_health`

## Carbon Integration

For ESG-aware sourcing decisions, combine with:
`assess_supply_chain_carbon(scope3_category="cat_1_purchased_goods")`"""
                            )
                        )
                    ]
                )
            elif name == "sustainability_planning_guide":
                focus_area = arguments.get("focus_area", "carbon_calculation") if arguments else "carbon_calculation"
                return GetPromptResult(
                    description=f"Sustainability and carbon-aware supply chain planning - {focus_area}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""# Sustainability-Embedded Supply Chain Planning

## Focus: {focus_area.replace('_', ' ').title()}

## Why Carbon-Aware Planning

Scope 3 emissions (supply chain) represent 70-90% of most companies' carbon footprint.
Regulators (EU CBAM, SEC climate disclosure, CSRD) are making Scope 3 reporting mandatory.
Carbon intensity is becoming a native planning parameter alongside cost and service level.

## Carbon Calculation Workflow

### Step 1: Identify Your Scope 3 Categories
Use `assess_supply_chain_carbon(scope3_category="cat_4_upstream_transport")` to get:
- Calculation methodology (tonne-km × emission factor)
- Required data inputs
- Relevant GHG Protocol guidance

### Step 2: Calculate Shipment Emissions
Use `assess_supply_chain_carbon` with weight and distance:
```
assess_supply_chain_carbon(
    transport_mode="road_truck_diesel",
    weight_tonnes=10.0,
    distance_km=500
)
```

### Step 3: Compare Modal Options
Use `assess_supply_chain_carbon(compare_modes=True, weight_tonnes=X, distance_km=Y)` to see
the full modal comparison and identify carbon reduction opportunities.

### Step 4: Embed in Routing Decisions
- Air → Rail shift: ~94% emission reduction (use for non-time-critical goods)
- Road → Rail shift: ~70% reduction (regional to continental lanes)
- LTL → FTL consolidation: 30-50% reduction per unit shipped

### Step 5: Supplier Carbon Scoring
Combine with `get_supplier_intelligence(risk_category="esg_scores")` to:
- Score suppliers on Scope 1+2 carbon intensity
- Prefer low-carbon suppliers in sourcing decisions
- Track Scope 3 Cat 1 (purchased goods) emissions

## Reporting Integration

- Connect carbon data to your ERP using `bridge_erp_context`
- Add `carbon_kg_co2e` field to shipment records via `normalize_carrier_tracking`
- Record carbon KPIs in `get_continuous_planning_template(planning_type="sop_integration")`

## Green Routing Recommendations

Use `assess_supply_chain_carbon` to identify optimal green corridors:
- Rotterdam → Duisburg (electrified Rhine rail)
- LA → Chicago (US intermodal)
- Singapore → Busan (efficient ocean lane)"""
                            )
                        )
                    ]
                )
            else:
                raise ValueError(f"Unknown prompt: {name}")

    async def _generate_contract(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Generate a contract specification"""
        component_name = arguments["component_name"]
        component_type = arguments["component_type"]
        requirements = arguments["requirements"]
        
        # Validate inputs
        if not self._validate_component_name(component_name):
            return [TextContent(
                type="text",
                text=f"Error: Invalid component name '{component_name}'. Must be a valid Python identifier."
            )]
        
        allowed_types = ["class", "function", "module", "service", "api"]
        if component_type not in allowed_types:
            return [TextContent(
                type="text",
                text=f"Error: Invalid component type '{component_type}'. Must be one of: {', '.join(allowed_types)}"
            )]
        
        if not isinstance(requirements, dict):
            return [TextContent(
                type="text",
                text="Error: Requirements must be a dictionary/object."
            )]
        
        contract_id = f"contract_{uuid.uuid4().hex[:8]}"
        
        contract = {
            "id": contract_id,
            "name": component_name,
            "type": component_type,
            "requirements": requirements,
            "generated_at": datetime.now().isoformat(),
            "interface": self._generate_interface(component_name, component_type, requirements),
            "constraints": self._extract_constraints(requirements),
            "validation_rules": self._generate_validation_rules(requirements)
        }
        
        self.contracts[contract_id] = contract
        
        result = f"""# Contract Generated: {component_name}

**Contract ID:** {contract_id}
**Type:** {component_type}
**Generated:** {contract["generated_at"]}

## Interface Definition
```python
{contract["interface"]}
```

## Constraints
{self._format_constraints(contract["constraints"])}

## Validation Rules
{self._format_validation_rules(contract["validation_rules"])}

## Next Steps
1. Review the contract to ensure it captures all requirements
2. Use this contract_id ({contract_id}) when implementing
3. Validate your implementation with `validate_implementation` tool

The contract has been saved and can be retrieved using `get_contract` tool."""
        
        return [TextContent(type="text", text=result)]

    async def _validate_implementation(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Validate code implementation against contract"""
        contract_id = arguments["contract_id"]
        code = arguments["code"]
        
        if contract_id not in self.contracts:
            return [TextContent(
                type="text",
                text=f"Error: Contract {contract_id} not found. Use `list_contracts` to see available contracts."
            )]
        
        contract = self.contracts[contract_id]
        validation_results = self._validate_code(code, contract)
        
        if validation_results["passed"]:
            result = f"""# ✓ Validation PASSED

**Contract:** {contract["name"]} ({contract_id})
**Implementation Status:** Valid

All checks passed:
- Interface compliance: ✓
- Constraint satisfaction: ✓
- Type correctness: ✓

The implementation satisfies all contract requirements."""
        else:
            errors = validation_results["errors"]
            result = f"""# ✗ Validation FAILED

**Contract:** {contract["name"]} ({contract_id})
**Errors Found:** {len(errors)}

## Issues to Fix:

{self._format_validation_errors(errors)}

## Recommended Actions:
1. Fix the errors listed above
2. Use `get_fix_suggestions` for guidance on similar errors
3. Re-validate after making changes

## Tips:
- Address errors in order of severity
- Check the contract interface for expected signatures
- Verify all constraints are met"""
        
        return [TextContent(type="text", text=result)]

    async def _record_error_pattern(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Record an error pattern for learning"""
        error_type = arguments["error_type"]
        code_before = arguments["code_before"]
        code_after = arguments["code_after"]
        context = arguments.get("context", {})
        
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = []
        
        pattern = {
            "id": f"pattern_{uuid.uuid4().hex[:8]}",
            "error_type": error_type,
            "code_before": code_before,
            "code_after": code_after,
            "context": context,
            "recorded_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.error_patterns[error_type].append(pattern)
        
        result = f"""# Error Pattern Recorded

**Pattern ID:** {pattern["id"]}
**Error Type:** {error_type}
**Recorded:** {pattern["recorded_at"]}

The fix pattern has been saved and will be used to provide suggestions for similar errors in the future.

**Total patterns for {error_type}:** {len(self.error_patterns[error_type])}

You can retrieve this pattern using `get_fix_suggestions` tool when encountering similar errors."""
        
        return [TextContent(type="text", text=result)]

    async def _get_fix_suggestions(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get fix suggestions based on error patterns"""
        error_type = arguments["error_type"]
        
        patterns = self.error_patterns.get(error_type, [])
        
        if not patterns:
            return [TextContent(
                type="text",
                text=f"""# No Historical Patterns Found

**Error Type:** {error_type}

No previous fixes have been recorded for this error type yet.

**Suggestions:**
1. Carefully review the error message
2. Check the contract specification
3. Look for similar patterns in the codebase
4. Once you fix it, use `record_error_pattern` to help future similar issues"""
            )]
        
        # Sort by usage count (most successful patterns first)
        sorted_patterns = sorted(patterns, key=lambda p: p["usage_count"], reverse=True)
        
        # Increment usage count for patterns being shown
        suggestions = []
        for i, pattern in enumerate(sorted_patterns[:3], 1):
            # Increment usage count to track popularity (how often patterns are shown to users)
            # Note: In a production system, consider only incrementing when user confirms the fix was helpful
            pattern["usage_count"] += 1
            
            before_code = self._smart_truncate(pattern["code_before"], self.MAX_BEFORE_AFTER_LENGTH)
            after_code = self._smart_truncate(pattern["code_after"], self.MAX_BEFORE_AFTER_LENGTH)
            
            suggestions.append(f"""
## Fix Pattern #{i} (Used {pattern["usage_count"]} times)

**Pattern ID:** {pattern["id"]}

### Before:
```python
{before_code}
```

### After:
```python
{after_code}
```

**Context:** {json.dumps(pattern.get("context", {}), indent=2)}
""")
        
        result = f"""# Fix Suggestions for {error_type}

**Found {len(patterns)} historical fix patterns**
**Showing top {min(3, len(patterns))} most successful fixes**

{chr(10).join(suggestions)}

## How to Apply:
1. Review the patterns above
2. Identify which one best matches your situation
3. Apply similar changes to your code
4. Validate the fix
5. Record your successful fix with `record_error_pattern`"""
        
        return [TextContent(type="text", text=result)]

    async def _add_example(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Add an example to the library"""
        example_type = arguments["example_type"]
        code = arguments["code"]
        description = arguments["description"]
        tags = arguments.get("tags", [])
        
        example = {
            "id": f"example_{uuid.uuid4().hex[:8]}",
            "type": example_type,
            "code": code,
            "description": description,
            "tags": tags,
            "added_at": datetime.now().isoformat()
        }
        
        self.examples.append(example)
        
        result = f"""# Example Added to Library

**Example ID:** {example["id"]}
**Type:** {example_type}
**Tags:** {', '.join(tags) if tags else 'None'}

The example has been saved and can be found using the `search_examples` tool.

**Total examples in library:** {len(self.examples)}"""
        
        return [TextContent(type="text", text=result)]

    async def _search_examples(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Search the example library"""
        query = arguments["query"].lower()
        example_type = arguments.get("example_type")
        tags = arguments.get("tags", [])
        
        matching_examples = []
        
        for example in self.examples:
            # Check type filter
            if example_type and example["type"] != example_type:
                continue
            
            # Check tags filter
            if tags and not any(tag in example["tags"] for tag in tags):
                continue
            
            # Check query match
            if (query in example["description"].lower() or 
                query in example["code"].lower() or
                any(query in tag.lower() for tag in example["tags"])):
                matching_examples.append(example)
        
        if not matching_examples:
            return [TextContent(
                type="text",
                text=f"""# No Examples Found

**Query:** {query}
**Type Filter:** {example_type or 'None'}
**Tag Filter:** {', '.join(tags) if tags else 'None'}

No examples match your search criteria. Try:
- Broader search terms
- Removing filters
- Adding examples with `add_example` tool"""
            )]
        
        results = []
        for example in matching_examples[:5]:  # Limit to top 5
            code_snippet = self._smart_truncate(example["code"], self.MAX_CODE_SNIPPET_LENGTH)
            
            results.append(f"""
## {example["id"]} - {example["type"]}

**Description:** {example["description"]}
**Tags:** {', '.join(example["tags"])}
**Added:** {example["added_at"]}

```python
{code_snippet}
```
""")
        
        result = f"""# Search Results

**Found {len(matching_examples)} matching examples**
**Showing top {min(5, len(matching_examples))}**

{chr(10).join(results)}"""
        
        return [TextContent(type="text", text=result)]

    async def _list_contracts(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """List all contracts"""
        if not self.contracts:
            return [TextContent(
                type="text",
                text="# No Contracts Available\n\nNo contracts have been generated yet. Use `generate_contract` tool to create one."
            )]
        
        contract_list = []
        for contract_id, contract in self.contracts.items():
            contract_list.append(f"""
- **{contract_id}**
  - Name: {contract["name"]}
  - Type: {contract["type"]}
  - Generated: {contract["generated_at"]}
""")
        
        result = f"""# Available Contracts

**Total Contracts:** {len(self.contracts)}

{chr(10).join(contract_list)}

Use `get_contract` with a contract ID to see full details."""
        
        return [TextContent(type="text", text=result)]

    async def _get_contract(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get a specific contract"""
        contract_id = arguments["contract_id"]
        
        if contract_id not in self.contracts:
            return [TextContent(
                type="text",
                text=f"Error: Contract {contract_id} not found. Use `list_contracts` to see available contracts."
            )]
        
        contract = self.contracts[contract_id]
        
        result = f"""# Contract Details: {contract["name"]}

**Contract ID:** {contract_id}
**Type:** {contract["type"]}
**Generated:** {contract["generated_at"]}

## Interface Definition
```python
{contract["interface"]}
```

## Constraints
{self._format_constraints(contract["constraints"])}

## Validation Rules
{self._format_validation_rules(contract["validation_rules"])}

## Requirements
```json
{json.dumps(contract["requirements"], indent=2)}
```"""
        
        return [TextContent(type="text", text=result)]

    async def _get_cis_principles(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get CIS principles and methodology guidelines"""
        principle = arguments.get("principle")
        
        if principle:
            if principle not in self.CIS_SEVEN_PRINCIPLES:
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown principle '{principle}'. Available: {', '.join(self.CIS_SEVEN_PRINCIPLES.keys())}"
                )]
            
            p = self.CIS_SEVEN_PRINCIPLES[principle]
            result = f"""# CIS Principle: {principle.replace('_', ' ').title()}

## Principle
{p['principle']}

## Implication for Code
{p['implication']}

## Code Pattern
{p['code_pattern']}

## How to Apply

When implementing this principle:
1. Design components that follow the principle's guidance
2. Validate your implementation adheres to the code pattern
3. Use `check_cis_compliance` to verify your code
4. Refer to `get_bible_section` for deeper understanding"""
        else:
            principles_list = []
            for name, p in self.CIS_SEVEN_PRINCIPLES.items():
                principles_list.append(f"""
### {name.replace('_', ' ').title()}
**Principle:** {p['principle']}
**Code Pattern:** {p['code_pattern']}
""")
            
            result = f"""# The Seven Principles of CIS (Circulatory Informatics System)

These principles guide the design of living, adaptive software systems inspired by biological organisms.

{chr(10).join(principles_list)}

## Usage

Use `get_cis_principles` with a specific principle name for detailed guidance:
- `get_cis_principles(principle="distributed_autonomy")`
- `get_cis_principles(principle="graceful_degradation")`

Use `check_cis_compliance` to validate your code against these principles."""
        
        return [TextContent(type="text", text=result)]

    async def _get_llm_coding_aid(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get guidance for common LLM coding issues"""
        issue_type = arguments.get("issue_type")
        
        if issue_type:
            if issue_type not in self.LLM_CODING_AIDS:
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown issue type '{issue_type}'. Available: {', '.join(self.LLM_CODING_AIDS.keys())}"
                )]
            
            aid = self.LLM_CODING_AIDS[issue_type]
            solutions_list = "\n".join([f"- {s}" for s in aid['solutions']])
            
            result = f"""# LLM Coding Aid: {issue_type.replace('_', ' ').title()}

## Problem Description
{aid['description']}

## Solutions
{solutions_list}

## Prevention Strategy

To prevent this issue in future code generation:
1. Include explicit constraints in your contracts
2. Provide working examples that demonstrate the correct approach
3. Use validation rules to catch violations
4. Record successful fixes with `record_error_pattern`

## Related CIS Principles

This issue relates to:
- **Memory and Learning**: Learn from past mistakes
- **Feedback-Driven Adaptation**: Use validation feedback to improve"""
        else:
            aids_list = []
            for name, aid in self.LLM_CODING_AIDS.items():
                aids_list.append(f"- **{name.replace('_', ' ').title()}**: {aid['description']}")
            
            result = f"""# LLM Coding Aids

Common issues encountered when using LLMs for code generation and their solutions.

## Available Aids

{chr(10).join(aids_list)}

## Usage

Get detailed guidance for a specific issue:
```
get_llm_coding_aid(issue_type="context_window_overflow")
get_llm_coding_aid(issue_type="hallucinated_imports")
```

## Integration with CIS

These aids integrate with the Circulatory Informatics System methodology:
- Use contracts to prevent issues upfront
- Validate implementations to catch issues
- Record patterns to learn from fixes"""
        
        return [TextContent(type="text", text=result)]

    async def _get_bible_section(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get a section from the Circulatory Informatics Bible"""
        section = arguments.get("section")
        if section is None:
            return [TextContent(
                type="text",
                text="Error: missing required argument 'section' for Bible lookup."
            )]
        if not self.bible_content:
            return [TextContent(
                type="text",
                text="""# Circulatory Informatics Bible

The Bible file was not found. Please ensure the 'Bible' file is present in the repository root.

## Core Concepts (Summary)

The Circulatory Informatics System treats software as a living organism:

1. **Biological Metaphors**: Systems are organisms, not machines
2. **The Seven Principles**: Distributed autonomy, continuous sensing, feedback-driven adaptation, emergent intelligence, memory and learning, graceful degradation, efficient resource flow
3. **The Nine Systems**: Each maps to a biological system (Circulatory, Digestive, Nervous, etc.)
4. **Vibe Coding**: Code that feels right - elegant, purposeful, aesthetically coherent

Use `get_cis_principles` for detailed principle guidance."""
            )]
        
        section_content = self._extract_bible_section(section)
        
        result = f"""# Circulatory Informatics Bible: {section.replace('_', ' ').title()}

{section_content}

---

## Other Available Sections

- `philosophy` - Philosophical foundations
- `seven_principles` - The Seven Principles of Living Code
- `nine_systems` - The Nine Systems architecture
- `vibe_coding` - How Living Code Achieves Vibe Coding
- `scientific_foundations` - Scientific foundations and research

Use `get_bible_section(section="<name>")` to access other sections."""
        
        return [TextContent(type="text", text=result)]

    async def _check_cis_compliance(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Check code for CIS principle compliance"""
        code = arguments["code"]
        component_description = arguments["component_description"]
        
        compliance_checks = []
        recommendations = []
        
        # Convert code to lowercase once for efficiency
        code_lower = code.lower()
        
        # Check for Distributed Autonomy indicators
        event_indicators = [
            r"\bevent[-_ ]?handler\b",
            r"\bon_?event\b",
            r"\bemit\b",
            r"\bpublish(er|ing)?\b",
            r"\bsubscribe(r|rs)?\b",
            r"\bmessage[-_ ]queue\b",
            r"\bmsg[-_ ]queue\b",
            r"\bqueue\.",          # method calls on queue-like objects
            r"\basync\s+def\b",
            r"\bawait\s+",
        ]
        has_event_patterns = any(re.search(pattern, code_lower) for pattern in event_indicators)
        compliance_checks.append({
            "principle": "Distributed Autonomy",
            "passed": has_event_patterns,
            "detail": "Event-driven or async patterns found" if has_event_patterns else "Consider adding event-driven patterns for decoupling"
        })
        if not has_event_patterns:
            recommendations.append("Add event-driven patterns (async/await, message queues) for better decoupling")
        
        # Check for Continuous Sensing (logging, monitoring) using word boundaries
        observability_pattern = re.compile(
            r"\b(?:log|logger|logging|metric|metrics|monitor|monitoring|trace|debug|info)\b",
            re.IGNORECASE,
        )
        has_observability = bool(observability_pattern.search(code))
        compliance_checks.append({
            "principle": "Continuous Sensing",
            "passed": has_observability,
            "detail": "Logging/monitoring patterns found" if has_observability else "Add logging and monitoring for observability"
        })
        if not has_observability:
            recommendations.append("Add logging statements for monitoring and debugging")
        
        # Check for Feedback-Driven Adaptation (error handling, retry)
        # Use regex for more flexible matching of try blocks
        error_handling_pattern = re.compile(
            r"\btry\s*:|except\b|\bretry\b|\bfallback\b|\brecover\b",
            re.IGNORECASE,
        )
        has_error_handling = bool(error_handling_pattern.search(code))
        compliance_checks.append({
            "principle": "Feedback-Driven Adaptation",
            "passed": has_error_handling,
            "detail": "Error handling patterns found" if has_error_handling else "Add try/except blocks and recovery mechanisms"
        })
        if not has_error_handling:
            recommendations.append("Add try/except blocks and implement retry/recovery logic")
        
        # Check for Graceful Degradation (fallbacks, timeouts)
        resilience_patterns = ['timeout', 'fallback', 'default_value', 'fallback_to', 'default_behavior', 'circuit', 'breaker', 'optional']
        has_resilience = any(pattern in code_lower for pattern in resilience_patterns)
        compliance_checks.append({
            "principle": "Graceful Degradation",
            "passed": has_resilience,
            "detail": "Resilience patterns found" if has_resilience else "Add fallback mechanisms and timeouts"
        })
        if not has_resilience:
            recommendations.append("Implement fallback mechanisms and timeouts for resilience")
        
        # Check for type hints (related to Emergent Intelligence - clear interfaces)
        # Use regex to detect function/method signatures with type hints
        type_hint_pattern = re.compile(
            r'def\s+\w+\s*\([^)]*:\s*\w+[^)]*\)|def\s+\w+\s*\([^)]*\)\s*->'
        )
        has_type_hints = bool(type_hint_pattern.search(code)) or 'typing' in code_lower
        compliance_checks.append({
            "principle": "Emergent Intelligence (Clear Interfaces)",
            "passed": has_type_hints,
            "detail": "Type hints found" if has_type_hints else "Add type hints for clear interfaces"
        })
        if not has_type_hints:
            recommendations.append("Add type hints for clearer interfaces between components")
        
        # Check for Memory and Learning (caching, history, patterns)
        memory_patterns = [
            r"\bcache\b", r"\bcached\b", r"\bmemoiz", r"\bhistory\b", 
            r"\bpattern\b", r"\blearn", r"\bstore\b", r"\bremember\b"
        ]
        has_memory = any(re.search(pattern, code_lower) for pattern in memory_patterns)
        compliance_checks.append({
            "principle": "Memory and Learning",
            "passed": has_memory,
            "detail": "Memory/learning patterns found" if has_memory else "Consider adding caching or learning from past events"
        })
        if not has_memory:
            recommendations.append("Consider implementing caching or learning from historical patterns")
        
        # Check for Efficient Resource Flow (pooling, lazy loading, scaling)
        resource_patterns = [
            r"\bpool\b", r"\bpooling\b", r"\blazy\b", r"\bscale\b", 
            r"\bthrottle\b", r"\brate[-_ ]?limit\b", r"\bbatch\b"
        ]
        has_resource_flow = any(re.search(pattern, code_lower) for pattern in resource_patterns)
        compliance_checks.append({
            "principle": "Efficient Resource Flow",
            "passed": has_resource_flow,
            "detail": "Resource management patterns found" if has_resource_flow else "Consider adding resource pooling or demand-based scaling"
        })
        if not has_resource_flow:
            recommendations.append("Consider implementing resource pooling, lazy loading, or demand-based scaling")
        
        # Calculate compliance score
        passed_count = sum(1 for c in compliance_checks if c['passed'])
        total_count = len(compliance_checks)
        compliance_score = (passed_count / total_count) * 100 if total_count > 0 else 0
        
        # Format results
        checks_output = []
        for check in compliance_checks:
            status = "✅" if check['passed'] else "❌"
            checks_output.append(f"{status} **{check['principle']}**: {check['detail']}")
        
        recommendations_output = "\n".join([f"- {r}" for r in recommendations]) if recommendations else "No recommendations - code follows CIS principles well!"
        
        result = f"""# CIS Compliance Check

## Component
{component_description}

## Compliance Score: {compliance_score:.0f}% ({passed_count}/{total_count} principles)

## Principle Checks

{chr(10).join(checks_output)}

## Recommendations

{recommendations_output}

## Next Steps

1. Address the recommendations above
2. Use `get_cis_principles` for detailed guidance on specific principles
3. Re-run `check_cis_compliance` after making changes
4. Use `get_llm_coding_aid` if you encounter implementation issues"""
        
        return [TextContent(type="text", text=result)]

    async def _get_base_network_info(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get Base L2 network configuration and details"""
        network = arguments.get("network")

        if network:
            if network not in self.BASE_NETWORK_CONFIG:
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown network '{network}'. Available: {', '.join(self.BASE_NETWORK_CONFIG.keys())}"
                )]

            config = self.BASE_NETWORK_CONFIG[network]
            result = f"""# Base Network: {config['name']}

## Network Details

| Property | Value |
|----------|-------|
| **Chain ID** | {config['chain_id']} |
| **RPC URL** | {config['rpc_url']} |
| **Block Explorer** | {config['block_explorer']} |
| **Bridge** | {config['bridge']} |
| **Currency** | {config['currency']} |
| **Layer** | {config['layer']} |
| **Avg Block Time** | {config['avg_block_time']} |
| **Avg Gas Cost** | {config['avg_gas_cost']} |

## Description
{config['description']}

## Quick Setup

### Add to MetaMask/Wallet
```
Network Name: {config['name']}
RPC URL: {config['rpc_url']}
Chain ID: {config['chain_id']}
Currency Symbol: ETH
Block Explorer: {config['block_explorer']}
```

### Hardhat Configuration
```javascript
networks: {{
  base{'' if network == 'mainnet' else '-sepolia'}: {{
    url: "{config['rpc_url']}",
    chainId: {config['chain_id']},
    accounts: [process.env.PRIVATE_KEY]
  }}
}}
```

## Next Steps
- Use `generate_supply_chain_contract` to create smart contracts for Base
- Use `get_business_onboarding_guide` for adoption guidance
- Use `get_supply_chain_templates` to browse available templates"""
        else:
            networks_info = []
            for net_name, config in self.BASE_NETWORK_CONFIG.items():
                networks_info.append(f"""
### {config['name']}
- **Chain ID:** {config['chain_id']}
- **RPC URL:** {config['rpc_url']}
- **Block Explorer:** {config['block_explorer']}
- **Avg Gas Cost:** {config['avg_gas_cost']}
- {config['description']}
""")

            result = f"""# Base L2 Network Information

Base is a secure, low-cost, builder-friendly Ethereum L2 built to bring the next billion users onchain.

## Available Networks

{chr(10).join(networks_info)}

## Why Base for Supply Chain?

1. **Ultra-low transaction costs** (< $0.01) make per-item tracking economically viable
2. **Fast confirmations** (~2s) enable real-time supply chain updates
3. **Ethereum security** provides enterprise-grade trust and reliability
4. **Growing ecosystem** with DeFi, NFTs, and business tooling
5. **No platform fees** — only pay gas for transactions you make

## Usage

Get detailed info for a specific network:
```
get_base_network_info(network="mainnet")
get_base_network_info(network="sepolia")
```"""

        return [TextContent(type="text", text=result)]

    async def _generate_supply_chain_contract(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Generate a supply chain smart contract template"""
        template_type = arguments["template_type"]
        business_name = arguments.get("business_name", "MyBusiness")

        if template_type not in self.SUPPLY_CHAIN_TEMPLATES:
            return [TextContent(
                type="text",
                text=f"Error: Unknown template type '{template_type}'. Available: {', '.join(self.SUPPLY_CHAIN_TEMPLATES.keys())}"
            )]

        template = self.SUPPLY_CHAIN_TEMPLATES[template_type]

        result = f"""# Supply Chain Smart Contract: {template['name']}

**Template:** {template_type}
**Business:** {business_name}
**Platform:** Base L2 (Ethereum Layer 2)
**Description:** {template['description']}

## Use Cases
{chr(10).join(f'- {uc}' for uc in template['use_cases'])}

## Solidity Contract

```solidity
{template['solidity_template']}
```

## Deployment Guide

### Prerequisites
- Node.js 18+ and npm
- A wallet with ETH on Base (testnet or mainnet)
- Hardhat or Foundry development framework

### Deploy with Hardhat
```bash
# Install dependencies
npm install hardhat @nomicfoundation/hardhat-toolbox

# Compile contract
npx hardhat compile

# Deploy to Base Sepolia testnet
npx hardhat run scripts/deploy.js --network base-sepolia

# Deploy to Base mainnet
npx hardhat run scripts/deploy.js --network base
```

### Verify on BaseScan
```bash
npx hardhat verify --network base-sepolia <CONTRACT_ADDRESS>
```

## Customization Tips
1. Modify struct fields to match your specific data requirements
2. Add access control for multi-role supply chains
3. Implement batch operations for high-volume use cases
4. Add off-chain data references (IPFS hashes) for detailed records
5. Consider upgradeable proxy patterns for future modifications

## Next Steps
1. Review and customize the contract for your needs
2. Use `validate_smart_contract` to check for issues
3. Deploy to Base Sepolia testnet for testing
4. Use `get_business_onboarding_guide` for integration guidance
5. Deploy to Base mainnet when ready"""

        return [TextContent(type="text", text=result)]

    async def _get_supply_chain_templates(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """List all available supply chain templates"""
        templates_list = []
        for key, template in self.SUPPLY_CHAIN_TEMPLATES.items():
            use_cases = "\n".join(f"  - {uc}" for uc in template["use_cases"])
            templates_list.append(f"""
### {template['name']} (`{key}`)
**Description:** {template['description']}
**Use Cases:**
{use_cases}
""")

        result = f"""# Supply Chain Smart Contract Templates

**Platform:** Base L2 (Ethereum Layer 2)
**Total Templates:** {len(self.SUPPLY_CHAIN_TEMPLATES)}

These templates are production-ready Solidity smart contracts designed for
supply chain management on Base L2, optimized for low gas costs and
small business accessibility.

{chr(10).join(templates_list)}

## How to Use

1. Browse the templates above to find your match
2. Generate a contract: `generate_supply_chain_contract(template_type="product_tracking")`
3. Validate the code: `validate_smart_contract(code="...")`
4. Follow the deployment guide in the generated output

## Custom Contracts

Need something different? Use the templates as starting points and:
- Combine features from multiple templates
- Add custom business logic
- Use `check_cis_compliance` to ensure robust design
- Use `validate_smart_contract` for security checks"""

        return [TextContent(type="text", text=result)]

    async def _get_business_onboarding_guide(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get business onboarding guide for blockchain adoption"""
        guide_section = arguments.get("guide_section")
        business_type = arguments.get("business_type")

        if guide_section and guide_section in self.BUSINESS_ONBOARDING:
            guide = self.BUSINESS_ONBOARDING[guide_section]

            if guide_section == "use_case_guide" and business_type:
                use_cases = guide.get("use_cases", {})
                if business_type in use_cases:
                    uc = use_cases[business_type]
                    contracts_list = ", ".join(f"`{c}`" for c in uc["recommended_contracts"])
                    result = f"""# Supply Chain Guide: {business_type.replace('_', ' ').title()} Business

## Overview
{uc['description']}

## Recommended Smart Contracts
{contracts_list}

## Estimated Setup Time
{uc['estimated_setup_time']}

## Getting Started
1. Generate your contracts: Use `generate_supply_chain_contract` for each recommended template
2. Test on Base Sepolia testnet
3. Integrate with your existing systems
4. Deploy to Base mainnet

## Next Steps
- Use `get_base_network_info` for network details
- Use `get_business_onboarding_guide(guide_section="integration_guide")` for integration help
- Use `get_business_onboarding_guide(guide_section="cost_analysis")` for cost details"""
                else:
                    available = ", ".join(use_cases.keys())
                    result = f"Error: Unknown business type '{business_type}'. Available: {available}"
            elif guide_section == "use_case_guide":
                use_cases_list = []
                for btype, uc in guide.get("use_cases", {}).items():
                    contracts_str = ", ".join(f"`{c}`" for c in uc["recommended_contracts"])
                    use_cases_list.append(f"""
### {btype.replace('_', ' ').title()}
**Description:** {uc['description']}
**Recommended Contracts:** {contracts_str}
**Setup Time:** {uc['estimated_setup_time']}
""")
                result = f"""# {guide['title']}

{chr(10).join(use_cases_list)}

## Get Tailored Guidance
Use `get_business_onboarding_guide(guide_section="use_case_guide", business_type="retail")` for specific recommendations."""
            elif guide_section == "integration_guide":
                steps = "\n".join(guide["steps"])
                tools = "\n".join(f"- {t}" for t in guide["recommended_tools"])
                result = f"""# {guide['title']}

## Integration Steps
{steps}

## Recommended Tools
{tools}

## Next Steps
- Use `generate_supply_chain_contract` to create your contracts
- Use `get_base_network_info` for network configuration
- Use `validate_smart_contract` to verify contract security"""
            else:
                items = guide.get("steps", guide.get("details", []))
                items_str = "\n".join(items)
                result = f"""# {guide['title']}

{items_str}

## Related Guides
- `get_business_onboarding_guide(guide_section="getting_started")` - Setup steps
- `get_business_onboarding_guide(guide_section="cost_analysis")` - Cost breakdown
- `get_business_onboarding_guide(guide_section="use_case_guide")` - Use case recommendations
- `get_business_onboarding_guide(guide_section="integration_guide")` - Integration help"""
        else:
            sections_list = []
            for key, guide in self.BUSINESS_ONBOARDING.items():
                sections_list.append(f"- **{key}**: {guide['title']}")

            result = f"""# Small Business Blockchain Onboarding

## Available Guide Sections

{chr(10).join(sections_list)}

## Quick Start

1. Start with `get_business_onboarding_guide(guide_section="getting_started")`
2. Review costs: `get_business_onboarding_guide(guide_section="cost_analysis")`
3. Find your use case: `get_business_onboarding_guide(guide_section="use_case_guide")`
4. Plan integration: `get_business_onboarding_guide(guide_section="integration_guide")`

## Why Blockchain on Base L2?

- **Ultra-low costs**: < $0.01 per transaction
- **Fast**: ~2 second confirmations
- **Secure**: Built on Ethereum
- **Accessible**: No monthly subscriptions or platform fees"""

        return [TextContent(type="text", text=result)]

    async def _validate_smart_contract(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Validate Solidity smart contract code"""
        code = arguments["code"]
        contract_type = arguments.get("contract_type", "custom")

        issues = []
        recommendations = []
        code_lower = code.lower()

        # Check for SPDX license identifier
        if "spdx-license-identifier" not in code_lower:
            issues.append({
                "severity": "medium",
                "type": "missing_license",
                "message": "Missing SPDX license identifier",
                "fix": "Add '// SPDX-License-Identifier: MIT' at the top of the file",
            })

        # Check for pragma solidity version
        pragma_match = re.search(r'pragma\s+solidity\s+[\^~>=<]*\s*(\d+)\.(\d+)(?:\.(\d+))?', code)
        if not pragma_match:
            issues.append({
                "severity": "high",
                "type": "missing_pragma",
                "message": "Missing or invalid Solidity pragma version",
                "fix": "Add 'pragma solidity ^0.8.19;' at the top of the file",
            })
        else:
            major = int(pragma_match.group(1))
            minor = int(pragma_match.group(2))
            version_str = f"{major}.{minor}" + (f".{pragma_match.group(3)}" if pragma_match.group(3) else "")
            if major == 0 and minor < 8:
                issues.append({
                    "severity": "high",
                    "type": "old_solidity_version",
                    "message": f"Solidity version {version_str} is outdated; use 0.8.x+ for built-in overflow protection",
                    "fix": "Update pragma to 'pragma solidity ^0.8.19;' for safety features",
                })

        # Check for reentrancy patterns
        if re.search(r'\.call\s*\{', code) or ".call{" in code:
            if "reentrancyguard" not in code_lower and "nonreentrant" not in code_lower:
                # Check if state changes happen after external call within the same function
                call_match = re.search(r'\.call\s*\{', code)
                if call_match:
                    call_pos = call_match.start()
                    # Scope to the next closing brace of the function (approximation)
                    next_func = code.find("function ", call_pos + 1)
                    scope_end = next_func if next_func != -1 else len(code)
                    after_call = code[call_pos:scope_end]
                    # Look for state-changing assignments (exclude local variable declarations)
                    if re.search(r'\b\w+\[\w+\]\s*[.=]|\b\w+\.\w+\s*=', after_call):
                        issues.append({
                            "severity": "critical",
                            "type": "potential_reentrancy",
                            "message": "Potential reentrancy vulnerability: state changes after external call",
                            "fix": "Use checks-effects-interactions pattern or OpenZeppelin ReentrancyGuard",
                        })

        # Check for unchecked return values on transfers
        if ".transfer(" in code:
            recommendations.append("Consider using .call{value: amount}('') instead of .transfer() for future compatibility")

        # Check for access control
        # Look for concrete authorization patterns rather than generic modifiers
        access_patterns = [
            "onlyowner",          # OpenZeppelin Ownable-style modifier
            "onlyrole",           # OpenZeppelin AccessControl-style modifier
            "hasrole(",           # AccessControl role checks
            "accesscontrol",      # Inheritance from AccessControl
            "ownable",            # Inheritance from Ownable
        ]
        # Explicit require checks on msg.sender, e.g. require(msg.sender == owner)
        has_sender_require = bool(re.search(r'require\s*\(\s*msg\.sender\s*==', code_lower))
        has_access_control = has_sender_require or any(p in code_lower for p in access_patterns)
        has_function_declarations = bool(re.search(r'\bfunction\s+\w+\s*\(', code))
        if not has_access_control and has_function_declarations:
            issues.append({
                "severity": "high",
                "type": "missing_access_control",
                "message": "No access control patterns detected",
                "fix": "Add modifiers (onlyOwner, role-based) or require checks (e.g., require(msg.sender == owner)) to restrict sensitive functions",
            })

        # Check for events
        if "event " not in code:
            issues.append({
                "severity": "medium",
                "type": "missing_events",
                "message": "No events defined for state changes",
                "fix": "Add events for important state changes to enable off-chain monitoring",
            })
        elif "emit " not in code:
            issues.append({
                "severity": "medium",
                "type": "events_not_emitted",
                "message": "Events defined but never emitted",
                "fix": "Emit events in functions that change state",
            })

        # Check for input validation
        has_require = re.search(r'\brequire\s*\(', code)
        has_revert = re.search(r'\brevert\s*\(', code)
        if not has_require and not has_revert:
            issues.append({
                "severity": "high",
                "type": "missing_input_validation",
                "message": "No input validation (require/revert) statements found",
                "fix": "Add require() statements to validate function inputs",
            })

        # Check for address(0) checks
        if "address" in code_lower and "address(0)" not in code:
            if re.search(r'\baddress\s+_\w+', code):
                recommendations.append("Consider adding address(0) checks for address parameters")

        # Base L2 specific recommendations
        recommendations.append("Base L2 has low gas costs — consider adding more detailed event data for better off-chain indexing")

        if "mapping" in code:
            recommendations.append("For large mappings on Base, consider pagination patterns for gas-efficient reads")

        # Supply chain specific checks
        if contract_type in ["product_tracking", "supplier_registry"]:
            if "timestamp" not in code_lower and "block.timestamp" not in code:
                recommendations.append("Supply chain contracts benefit from timestamp tracking for audit trails")

        # Calculate validation score
        critical_count = sum(1 for i in issues if i["severity"] == "critical")
        high_count = sum(1 for i in issues if i["severity"] == "high")
        medium_count = sum(1 for i in issues if i["severity"] == "medium")
        low_count = sum(1 for i in issues if i["severity"] == "low")

        total_issues = len(issues)
        if total_issues == 0:
            score = 100
        else:
            score = max(0, 100 - (critical_count * 30) - (high_count * 15) - (medium_count * 5) - (low_count * 2))

        # Format issues
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
        }

        issues_output = []
        for issue in sorted(issues, key=lambda x: ["critical", "high", "medium", "low"].index(x["severity"])):
            emoji = severity_emoji.get(issue["severity"], "⚪")
            issues_output.append(f"""
### {emoji} {issue['type']} ({issue['severity']})
**Issue:** {issue['message']}
**Fix:** {issue['fix']}
""")

        recs_output = "\n".join(f"- {r}" for r in recommendations) if recommendations else "No additional recommendations."

        passed = total_issues == 0
        status = "✅ PASSED" if passed else "⚠️ ISSUES FOUND"

        result = f"""# Smart Contract Validation: {status}

## Validation Score: {score}/100

**Contract Type:** {contract_type}
**Platform:** Base L2
**Issues Found:** {total_issues} ({critical_count} critical, {high_count} high, {medium_count} medium, {low_count} low)

## Issues

{chr(10).join(issues_output) if issues_output else "No issues found! Contract follows best practices."}

## Recommendations

{recs_output}

## Next Steps

1. {"Address critical and high severity issues before deployment" if not passed else "Contract is ready for testing"}
2. Deploy to Base Sepolia testnet for functional testing
3. Consider a professional audit for production contracts
4. Use `get_base_network_info` for deployment configuration"""

        return [TextContent(type="text", text=result)]

    async def _get_supplier_intelligence(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Return supplier risk assessment framework and signals"""
        risk_category = arguments.get("risk_category")
        supplier_name = arguments.get("supplier_name", "")
        industry = arguments.get("industry", "")

        header = "# Supplier Intelligence Risk Assessment"
        if supplier_name:
            header += f" — {supplier_name}"
        if industry:
            header += f" ({industry})"

        if risk_category and risk_category in self.SUPPLIER_RISK_FACTORS:
            data = self.SUPPLIER_RISK_FACTORS[risk_category]
            signals_txt = "\n".join(f"- {s}" for s in data["signals"])
            risk_levels_txt = "\n".join(
                f"- **{level.upper()}**: {desc}" for level, desc in data["risk_levels"].items()
            )
            sources_txt = "\n".join(f"- {src}" for src in data["data_sources"])
            result = f"""{header}

## {data['title']}

### Risk Signals to Monitor
{signals_txt}

### Risk Level Definitions
{risk_levels_txt}

### Recommended Data Sources
{sources_txt}

## Next Steps

- Combine with `get_continuous_planning_template(planning_type="constraint_management")` to build a constrained supply plan when risk is high
- Use `bridge_erp_context` to pull OTD and order history from your ERP for lead_time_variance scoring
- Connect ESG scores to `assess_supply_chain_carbon` for Scope 3 Cat 1 visibility"""
        else:
            sections = []
            for key, data in self.SUPPLIER_RISK_FACTORS.items():
                signals_txt = "\n".join(f"  - {s}" for s in data["signals"][:3])
                sections.append(
                    f"### {data['title']}\n**Tool:** `get_supplier_intelligence(risk_category=\"{key}\")`\n"
                    f"**Key signals (top 3):**\n{signals_txt}"
                )
            all_sections = "\n\n".join(sections)
            result = f"""{header}

## Overview

Supplier risk spans four dimensions. Use `risk_category` to drill into each one.

{all_sections}

## Integrated Workflow

1. Score all Tier-1 suppliers across all four dimensions
2. Flag suppliers with ≥2 HIGH or any CRITICAL rating for immediate review
3. Feed financial and lead-time risk into your constrained supply plan via `get_continuous_planning_template`
4. Include ESG scores in sourcing RFPs to drive Scope 3 reduction
5. Use `assess_supply_chain_carbon(scope3_category="cat_1_purchased_goods")` for purchased-goods emissions

## Data Sources Summary

| Dimension | Primary Sources |
|-----------|----------------|
| Financial Health | Dun & Bradstreet, Coface, Everstream Analytics |
| Geopolitical | Riskmethods, World Bank, OFAC |
| Lead Time | ERP order history, TMS, Port authority APIs |
| ESG | EcoVadis, CDP, Sustainalytics, MSCI ESG |"""

        return [TextContent(type="text", text=result)]

    async def _normalize_carrier_tracking(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Return carrier API details and normalized tracking schema"""
        carrier = arguments.get("carrier")
        use_case = arguments.get("use_case", "tracking_visibility")

        # Map use cases to the relevant endpoint key
        use_case_endpoint_map = {
            "tracking_visibility": "tracking",
            "rate_shopping": "rates",
            "shipment_booking": "ship",
            "webhook_events": "tracking",
        }
        relevant_endpoint_key = use_case_endpoint_map.get(use_case, "tracking")

        if carrier and carrier in self.CARRIER_APIS:
            data = self.CARRIER_APIS[carrier]
            endpoints_txt = "\n".join(
                f"- **{name}**: `{path}`" for name, path in data["key_endpoints"].items()
            )
            fields_txt = "\n".join(f"- `{f}`" for f in data["tracking_fields"])
            status_map_txt = "\n".join(
                f"- `{k}` → `{v}`" for k, v in data["normalized_status_map"].items()
            )
            modes_txt = ", ".join(data["modes"])
            primary_endpoint = data["key_endpoints"].get(relevant_endpoint_key, list(data["key_endpoints"].values())[0])
            result = f"""# {data['name']} API Integration Guide — {use_case.replace('_', ' ').title()}

## Authentication
**Method:** {data['auth']}
**Base URL:** `{data['base_url']}`

## Primary Endpoint for `{use_case}`
`{data['base_url']}{primary_endpoint}`

## All Key Endpoints
{endpoints_txt}

## Tracking Fields
{fields_txt}

## Normalized Status Map
Maps {data['name']}-specific codes to the unified tracking schema:
{status_map_txt}

## Supported Transport Modes
{modes_txt}

## Webhook Support
{"✅ Supported — subscribe to shipment events for real-time status updates" if data['webhook_support'] else "❌ Not supported — use polling"}

## Normalized Schema Integration

Map all `{carrier}` tracking responses to the unified schema using `normalize_carrier_tracking()`.
The unified schema includes `carrier`, `status` (normalized), `events`, `mode`, and `carbon_kg_co2e`.

## Next Steps

- Use `assess_supply_chain_carbon` to add `carbon_kg_co2e` to each shipment record
- Store normalized events in your ERP via `bridge_erp_context`
- Feed delivery performance into `get_supplier_intelligence(risk_category="lead_time_variance")`"""
        else:
            carriers_list = []
            for key, c in self.CARRIER_APIS.items():
                modes = ", ".join(c["modes"])
                carriers_list.append(
                    f"### {c['name']} (`{key}`)\n"
                    f"- **Auth**: {c['auth']}\n"
                    f"- **Base URL**: `{c['base_url']}`\n"
                    f"- **Modes**: {modes}\n"
                    f"- **Webhooks**: {'Yes' if c['webhook_support'] else 'No'}"
                )
            carriers_txt = "\n\n".join(carriers_list)

            schema_fields = "\n".join(
                f"- **`{k}`**: {v}" if not isinstance(v, dict) else f"- **`{k}`**: object with fields {list(v.keys())}"
                for k, v in self.NORMALIZED_TRACKING_SCHEMA.items()
            )
            result = f"""# Multi-Modal Carrier Visibility — Normalized Tracking Schema

## Why a Unified Schema?

Each carrier returns different field names, status codes, and date formats.
The normalized schema provides a single context layer for all carriers,
enabling agents to reason over shipments without carrier-specific logic.

## Normalized Shipment Schema

{schema_fields}

## Supported Carriers

{carriers_txt}

## Integration Pattern

```python
# Pseudocode — normalize any carrier response
def normalize_shipment(carrier: str, raw_response: dict) -> dict:
    status_map = CARRIER_APIS[carrier]["normalized_status_map"]
    return {{
        "carrier": carrier,
        "tracking_number": extract_tracking_number(raw_response, carrier),
        "status": status_map.get(raw_response.get("statusCode"), "unknown"),
        "events": normalize_events(raw_response, carrier),
        "carbon_kg_co2e": calculate_carbon(raw_response, carrier),
    }}
```

## Use Cases by Integration Type

| Use Case | Tool call |
|----------|-----------|
| Tracking visibility | `normalize_carrier_tracking(carrier="fedex", use_case="tracking_visibility")` |
| Rate shopping | `normalize_carrier_tracking(carrier="ups", use_case="rate_shopping")` |
| Booking | `normalize_carrier_tracking(carrier="maersk", use_case="shipment_booking")` |
| Real-time events | `normalize_carrier_tracking(use_case="webhook_events")` |

## Carbon Integration

Add `carbon_kg_co2e` to every shipment record:
`assess_supply_chain_carbon(transport_mode=..., weight_tonnes=..., distance_km=...)`"""

        return [TextContent(type="text", text=result)]

    async def _bridge_erp_context(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Return cross-ERP field mappings and integration guidance"""
        source_erp = arguments.get("source_erp")
        target_erp = arguments.get("target_erp")
        data_category = arguments.get("data_category", "all")

        if source_erp and target_erp:
            if source_erp not in self.ERP_SYSTEMS or target_erp not in self.ERP_SYSTEMS:
                unknown = source_erp if source_erp not in self.ERP_SYSTEMS else target_erp
                valid = ", ".join(self.ERP_SYSTEMS.keys())
                return [TextContent(type="text", text=f"Unknown ERP system: '{unknown}'. Valid options: {valid}")]

            src = self.ERP_SYSTEMS[source_erp]
            tgt = self.ERP_SYSTEMS[target_erp]

            if data_category != "all" and data_category in self.ERP_FIELD_MAPPINGS:
                categories = {data_category: self.ERP_FIELD_MAPPINGS[data_category]}
            else:
                categories = self.ERP_FIELD_MAPPINGS

            mapping_sections = []
            for cat_name, cat_data in categories.items():
                if source_erp in cat_data and target_erp in cat_data:
                    src_fields = cat_data[source_erp]
                    tgt_fields = cat_data[target_erp]
                    rows = "\n".join(
                        f"| {logical} | `{src_fields.get(logical, 'N/A')}` | `{tgt_fields.get(logical, 'N/A')}` |"
                        for logical in src_fields
                    )
                    mapping_sections.append(
                        f"### {cat_name.replace('_', ' ').title()}\n\n"
                        f"| Logical Field | {src['name']} | {tgt['name']} |\n"
                        f"|--------------|----------------|----------------|\n"
                        f"{rows}"
                    )

            mappings_txt = "\n\n".join(mapping_sections) if mapping_sections else "No field mappings available for the selected category."

            src_protocols = ", ".join(src["integration_protocols"])
            tgt_protocols = ", ".join(tgt["integration_protocols"])

            result = f"""# Cross-ERP Context Bridge: {src['name']} → {tgt['name']}

## Field Mappings

{mappings_txt}

## Integration Protocols

| System | Supported Protocols |
|--------|---------------------|
| {src['name']} | {src_protocols} |
| {tgt['name']} | {tgt_protocols} |

## Recommended Integration Approach

**{src['name']}:** {src['mcp_approach']}

**{tgt['name']}:** {tgt['mcp_approach']}

## Translation Pattern

```python
# Pseudocode — translate a purchase order between ERPs
def translate_po(source_po: dict, source_erp: str, target_erp: str) -> dict:
    mapping = ERP_FIELD_MAPPINGS["purchase_order"]
    src_map = mapping[source_erp]
    tgt_map = mapping[target_erp]
    return {{
        tgt_field: source_po.get(src_map[logical])
        for logical, tgt_field in tgt_map.items()
    }}
```

## Next Steps

- Use `normalize_carrier_tracking` to enrich shipment records before writing to target ERP
- Feed the translated data into `get_continuous_planning_template` for unified planning context
- Validate Scope 3 Cat 4 transport emissions via `assess_supply_chain_carbon`"""
        else:
            erp_list = []
            for key, erp in self.ERP_SYSTEMS.items():
                modules_txt = ", ".join(erp["modules"][:4]) + ("..." if len(erp["modules"]) > 4 else "")
                protocols_txt = ", ".join(erp["integration_protocols"])
                erp_list.append(
                    f"### {erp['name']} (`{key}`)\n"
                    f"- **Modules**: {modules_txt}\n"
                    f"- **Protocols**: {protocols_txt}\n"
                    f"- **MCP Approach**: {erp['mcp_approach']}"
                )
            erp_txt = "\n\n".join(erp_list)

            categories_txt = "\n".join(f"- `{c}`" for c in self.ERP_FIELD_MAPPINGS.keys())

            result = f"""# Cross-ERP Context Bridge

## The Problem

Most enterprises run multiple ERP systems simultaneously (SAP + Oracle + NetSuite + regional).
Each system uses different field names, data models, and integration protocols.
The Cross-ERP Context Bridge provides a neutral translation layer so agents can reason
across all systems with a shared context.

## Supported ERP Systems

{erp_txt}

## Available Data Categories for Mapping

{categories_txt}

## Usage

```
bridge_erp_context(
    source_erp="sap",
    target_erp="oracle",
    data_category="purchase_order"
)
```

## Integration Architecture

```
SAP OData  ──┐
Oracle REST──┼──► Neutral Context Layer (MCP) ──► Agent Reasoning
NetSuite SQL─┤
D365 OData ──┘
```

## Supported Field Mappings

{chr(10).join(f"- `{c}`: maps {', '.join(self.ERP_SYSTEMS.keys())}" for c in self.ERP_FIELD_MAPPINGS.keys())}

## Next Steps

- Use with `normalize_carrier_tracking` to bridge logistics data across ERPs
- Feed unified context into `get_continuous_planning_template` for cross-system planning
- Combine with `get_supplier_intelligence` for supplier master data normalization"""

        return [TextContent(type="text", text=result)]

    async def _get_continuous_planning_template(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Return continuous planning templates and manage in-memory planning sessions"""
        planning_type = arguments.get("planning_type")
        session_id = arguments.get("session_id")
        context_update = arguments.get("context_update")

        # Update or retrieve planning session if session_id provided
        session_info = ""
        if session_id:
            if session_id not in self.planning_sessions:
                self.planning_sessions[session_id] = {
                    "created": datetime.now().isoformat(),
                    "planning_type": planning_type,
                    "context": {},
                }
            session = self.planning_sessions[session_id]
            if context_update and isinstance(context_update, dict):
                session["context"].update(context_update)
                session["last_updated"] = datetime.now().isoformat()
            ctx_items = "\n".join(f"  - **{k}**: {v}" for k, v in session["context"].items())
            session_info = f"""
## Active Planning Session: `{session_id}`

- **Created**: {session.get('created', 'unknown')}
- **Last Updated**: {session.get('last_updated', 'not yet updated')}
- **Stored Context**:
{ctx_items if ctx_items else '  (empty — use context_update to add planning data)'}
"""

        if planning_type and planning_type in self.PLANNING_TEMPLATES:
            tpl = self.PLANNING_TEMPLATES[planning_type]
            inputs_txt = "\n".join(f"- {inp}" for inp in tpl["inputs"])
            outputs_txt = "\n".join(f"- {out}" for out in tpl["outputs"])
            context_fields_txt = "\n".join(f"- `{f}`" for f in tpl["mcp_context_fields"])
            result = f"""# Continuous Planning: {tpl['title']}
{session_info}
## Planning Horizon
**{tpl['horizon'].replace('_', ' ').title()}**
**Review Cadence**: {tpl['review_cadence']}

## Required Inputs
{inputs_txt}

## Planning Outputs
{outputs_txt}

## MCP Context Fields
These fields should be maintained in every planning session for this template:
{context_fields_txt}

## Session Management

Use `session_id` to maintain a persistent planning context across conversations:
```
get_continuous_planning_template(
    planning_type="{planning_type}",
    session_id="my-planning-session",
    context_update={{{", ".join(f'"{f}": <value>' for f in tpl['mcp_context_fields'][:3])}}}
)
```

## Integration with Other Tools

- **Supplier risk**: Feed `get_supplier_intelligence` outputs into `constraint_management` template
- **Carrier data**: Use `normalize_carrier_tracking` to populate in-transit inventory figures
- **ERP sync**: Use `bridge_erp_context` to read on-hand inventory and open orders
- **Carbon**: Add carbon KPIs via `assess_supply_chain_carbon` to the S&OP dashboard"""
        else:
            templates_list = []
            for key, tpl in self.PLANNING_TEMPLATES.items():
                inputs_preview = tpl["inputs"][0] if tpl["inputs"] else ""
                templates_list.append(
                    f"### {tpl['title']}\n"
                    f"- **Horizon**: {tpl['horizon'].replace('_', ' ').title()}\n"
                    f"- **Cadence**: {tpl['review_cadence']}\n"
                    f"- **Tool call**: `get_continuous_planning_template(planning_type=\"{key}\")`\n"
                    f"- **Sample input**: {inputs_preview}"
                )
            templates_txt = "\n\n".join(templates_list)
            active_sessions = len(self.planning_sessions)
            result = f"""# Continuous Planning Partner — Template Library
{session_info}
## What Is Continuous Planning?

Traditional planning is episodic — a monthly S&OP meeting, a weekly inventory review.
Continuous planning transforms the AI from a one-off query tool into a persistent planning
partner that maintains rolling context across demand signals, supply constraints, and financial targets.

MCP enables this by keeping context across planning cycles, so every decision builds on shared history.

## Active Planning Sessions

{active_sessions} session(s) currently active in memory.
Use `session_id` to create or resume a named session.

## Available Planning Templates

{templates_txt}

## Recommended Planning Hierarchy

1. **Demand Sensing** (weekly) → feeds into →
2. **Inventory Optimization** (daily) → drives →
3. **Constraint Management** (weekly) → rolls up into →
4. **S&OP Integration** (monthly)

## Getting Started

```
# Start a demand sensing session
get_continuous_planning_template(
    planning_type="demand_sensing",
    session_id="q1-2026-demand",
    context_update={{"sku_id": "SKU-001", "week": "2026-W01", "baseline_forecast": 500}}
)
```"""

        return [TextContent(type="text", text=result)]

    async def _assess_supply_chain_carbon(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Calculate Scope 3 carbon footprint and return carbon-aware routing recommendations"""
        transport_mode = arguments.get("transport_mode")
        weight_tonnes = arguments.get("weight_tonnes")
        distance_km = arguments.get("distance_km")
        scope3_category = arguments.get("scope3_category")
        compare_modes = arguments.get("compare_modes", False)

        # Carbon calculation section
        calc_section = ""
        if transport_mode and weight_tonnes is not None and distance_km is not None:
            if transport_mode in self.CARBON_EMISSION_FACTORS["transport_modes"]:
                mode_data = self.CARBON_EMISSION_FACTORS["transport_modes"][transport_mode]
                factor = mode_data["kg_co2e_per_tonne_km"]
                total_co2e = factor * float(weight_tonnes) * float(distance_km)
                calc_section = f"""
## Carbon Calculation Result

| Parameter | Value |
|-----------|-------|
| Transport Mode | {transport_mode.replace('_', ' ').title()} |
| Weight | {weight_tonnes} tonnes |
| Distance | {distance_km} km |
| Emission Factor | {factor} kg CO₂e / tonne-km |
| **Total Emissions** | **{total_co2e:.2f} kg CO₂e** |

*Source: GHG Protocol / GLEC Framework emission factors*
"""

        # Modal comparison
        comparison_section = ""
        if compare_modes and weight_tonnes is not None and distance_km is not None:
            rows = []
            for mode_key, mode_data in self.CARBON_EMISSION_FACTORS["transport_modes"].items():
                factor = mode_data["kg_co2e_per_tonne_km"]
                total = factor * float(weight_tonnes) * float(distance_km)
                rows.append((mode_key, total, mode_data["relative_impact"], mode_data["use_cases"]))
            rows.sort(key=lambda x: x[1])
            table_rows = "\n".join(
                f"| {r[0].replace('_', ' ').title()} | {r[1]:.2f} kg | {r[2].replace('_', ' ')} | {r[3]} |"
                for r in rows
            )
            comparison_section = f"""
## Modal Comparison ({weight_tonnes}t × {distance_km}km)

| Mode | CO₂e Emissions | Impact | Best For |
|------|---------------|--------|----------|
{table_rows}
"""

        # Scope 3 category section
        scope3_section = ""
        if scope3_category and scope3_category in self.CARBON_EMISSION_FACTORS["scope3_categories"]:
            cat = self.CARBON_EMISSION_FACTORS["scope3_categories"][scope3_category]
            data_needed_txt = "\n".join(f"- {d}" for d in cat["data_needed"])
            scope3_section = f"""
## Scope 3 Category: {scope3_category.replace('_', ' ').title()}

**Description**: {cat['description']}

**Calculation Method**: {cat['calculation_method']}

**Data Required**:
{data_needed_txt}
"""
        elif not scope3_category and not transport_mode:
            cats = self.CARBON_EMISSION_FACTORS["scope3_categories"]
            cat_rows = "\n".join(
                f"| `{k}` | {v['description']} | {v['calculation_method'][:60]}... |"
                for k, v in cats.items()
            )
            scope3_section = f"""
## Scope 3 Supply Chain Categories

| Category | Description | Method |
|----------|-------------|--------|
{cat_rows}

Use `scope3_category=<category>` to get full details and data requirements.
"""

        # Routing recommendations
        tradeoffs = self.CARBON_EMISSION_FACTORS["routing_optimization"]["carbon_vs_cost_tradeoffs"]
        corridors = self.CARBON_EMISSION_FACTORS["routing_optimization"]["green_corridors"]
        tradeoffs_txt = "\n".join(f"- {t}" for t in tradeoffs)
        corridors_txt = "\n".join(f"- {c}" for c in corridors)

        # Transport modes summary (when no specific mode requested)
        modes_summary = ""
        if not transport_mode:
            mode_rows = "\n".join(
                f"| {k.replace('_', ' ').title()} | {v['kg_co2e_per_tonne_km']} | {v['relative_impact'].replace('_', ' ')} |"
                for k, v in self.CARBON_EMISSION_FACTORS["transport_modes"].items()
            )
            modes_summary = f"""
## Emission Factors by Transport Mode

| Mode | kg CO₂e / tonne-km | Relative Impact |
|------|-------------------|----------------|
{mode_rows}

*Source: GHG Protocol GLEC Framework 2.0*
"""

        result = f"""# Supply Chain Carbon Assessment
{calc_section}{comparison_section}{scope3_section}{modes_summary}
## Carbon-Aware Routing Trade-offs

{tradeoffs_txt}

## High-Efficiency Green Corridors

{corridors_txt}

## Integration with Planning

- Add `carbon_kg_co2e` to shipment records via `normalize_carrier_tracking`
- Set carbon budget constraints in `get_continuous_planning_template(planning_type="constraint_management")`
- Score suppliers on Scope 1+2 intensity via `get_supplier_intelligence(risk_category="esg_scores")`
- Report Scope 3 Cat 4 in your S&OP dashboard via `get_continuous_planning_template(planning_type="sop_integration")`

## Regulatory Context

- **EU CBAM**: Carbon Border Adjustment Mechanism — requires Scope 3 data for imports
- **CSRD**: EU Corporate Sustainability Reporting Directive — mandatory Scope 3 from 2025
- **SEC Climate Disclosure**: Proposed Scope 3 disclosure for large US public companies
- **Science-Based Targets (SBTi)**: Requires Scope 3 reduction pathway for net-zero commitments"""

        return [TextContent(type="text", text=result)]

    # Helper methods
    
    def _validate_component_name(self, name: str) -> bool:
        """Validate that component name is a valid Python identifier"""
        if not name or not isinstance(name, str):
            return False
        # Check if it's a valid Python identifier
        return name.isidentifier()
    
    def _generate_interface(self, name: str, component_type: str, requirements: Dict[str, Any]) -> str:
        """Generate interface code based on component type"""
        if component_type == "class":
            methods = requirements.get("methods", [])
            properties = requirements.get("properties", [])
            
            interface = f"class {name}:\n"
            interface += '    """' + requirements.get("description", f"{name} class") + '"""\n\n'
            
            if properties:
                interface += "    def __init__(self):\n"
                for prop in properties:
                    interface += f"        self.{prop}: Any = None\n"
                interface += "\n"
            
            for method in methods:
                params = method.get("parameters", [])
                param_str = ", ".join([f"{p['name']}: {p.get('type', 'Any')}" for p in params])
                return_type = method.get("return_type", "None")
                interface += f"    def {method['name']}(self, {param_str}) -> {return_type}:\n"
                interface += f'        """{method.get("description", "")}"""\n'
                interface += "        pass\n\n"
            
            return interface
            
        elif component_type == "function":
            params = requirements.get("parameters", [])
            param_str = ", ".join([f"{p['name']}: {p.get('type', 'Any')}" for p in params])
            return_type = requirements.get("return_type", "None")
            
            interface = f"def {name}({param_str}) -> {return_type}:\n"
            interface += '    """' + requirements.get("description", f"{name} function") + '"""\n'
            interface += "    pass\n"
            
            return interface
        
        else:
            return f"# {component_type}: {name}\n# Interface to be defined based on requirements"

    def _extract_constraints(self, requirements: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract constraints from requirements"""
        constraints = {
            "type_constraints": [],
            "validation_constraints": [],
            "behavioral_constraints": []
        }
        
        if "constraints" in requirements:
            for constraint in requirements["constraints"]:
                if isinstance(constraint, dict):
                    category = constraint.get("category", "behavioral_constraints")
                    constraints[category].append(constraint.get("rule", str(constraint)))
                else:
                    constraints["behavioral_constraints"].append(str(constraint))
        
        return constraints

    def _generate_validation_rules(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate validation rules"""
        rules = []
        
        # Add interface validation
        rules.append({
            "type": "interface_check",
            "description": "Verify all required methods/functions are present",
            "severity": "critical"
        })
        
        # Add type validation
        rules.append({
            "type": "type_check",
            "description": "Verify type hints match specification",
            "severity": "high"
        })
        
        # Add constraint validation
        if "constraints" in requirements:
            rules.append({
                "type": "constraint_check",
                "description": "Verify all constraints are satisfied",
                "severity": "critical"
            })
        
        return rules

    def _format_constraints(self, constraints: Dict[str, List[str]]) -> str:
        """Format constraints for display"""
        if not any(constraints.values()):
            return "No specific constraints defined."
        
        formatted = []
        for category, rules in constraints.items():
            if rules:
                formatted.append(f"\n### {category.replace('_', ' ').title()}")
                for i, rule in enumerate(rules, 1):
                    formatted.append(f"{i}. {rule}")
        
        return "\n".join(formatted)

    def _format_validation_rules(self, rules: List[Dict[str, Any]]) -> str:
        """Format validation rules for display"""
        if not rules:
            return "No validation rules defined."
        
        formatted = []
        for i, rule in enumerate(rules, 1):
            severity = rule.get("severity", "medium")
            formatted.append(f"{i}. **{rule['type']}** ({severity})")
            formatted.append(f"   {rule['description']}")
        
        return "\n".join(formatted)

    def _validate_code(self, code: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Validate code against contract using AST parsing for accuracy"""
        errors = []
        
        # Try to parse the code with AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            errors.append({
                "type": "syntax_error",
                "severity": "critical",
                "message": f"Syntax error in code: {str(e)}",
                "line": e.lineno if hasattr(e, 'lineno') else 0,
                "fix_suggestion": "Fix syntax errors in the code"
            })
            return {
                "passed": False,
                "errors": errors
            }
        
        # Find the component in the AST
        component_found = False
        component_has_docstring = False
        
        for node in ast.walk(tree):
            # Check for class or function definition matching the contract
            if contract["type"] == "class" and isinstance(node, ast.ClassDef):
                if node.name == contract["name"]:
                    component_found = True
                    # Check for class docstring
                    component_has_docstring = ast.get_docstring(node) is not None
                    
                    # For classes, check methods have type hints
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Check if method has return type annotation
                            # Skip dunder methods (special methods) as they commonly omit return annotations
                            is_dunder = item.name.startswith("__") and item.name.endswith("__")
                            if item.returns is None and not is_dunder:
                                errors.append({
                                    "type": "type_hint_missing",
                                    "severity": "high",
                                    "message": f"Method '{item.name}' missing return type annotation",
                                    "line": item.lineno,
                                    "fix_suggestion": f"Add return type annotation to method '{item.name}'"
                                })
                    
            elif contract["type"] == "function" and isinstance(node, ast.FunctionDef):
                if node.name == contract["name"]:
                    component_found = True
                    # Check for function docstring
                    component_has_docstring = ast.get_docstring(node) is not None
                    
                    # Check for return type annotation
                    if node.returns is None:
                        errors.append({
                            "type": "type_hint_missing",
                            "severity": "high",
                            "message": "Return type annotation missing",
                            "line": node.lineno,
                            "fix_suggestion": "Add return type annotation (-> ReturnType)"
                        })
        
        # Check if component was found
        if not component_found:
            errors.append({
                "type": "interface_violation",
                "severity": "critical",
                "message": f"Component '{contract['name']}' not found in implementation",
                "line": 0,
                "fix_suggestion": f"Ensure your code defines '{contract['name']}' as a {contract['type']}"
            })
        
        # Check for docstring
        if component_found and not component_has_docstring:
            errors.append({
                "type": "documentation_missing",
                "severity": "medium",
                "message": f"{contract['type'].capitalize()} '{contract['name']}' is missing a docstring",
                "line": 0,
                "fix_suggestion": f"Add a docstring to document the {contract['type']}"
            })
        
        return {
            "passed": len(errors) == 0,
            "errors": errors
        }

    def _format_validation_errors(self, errors: List[Dict[str, Any]]) -> str:
        """Format validation errors for display"""
        formatted = []
        
        for i, error in enumerate(errors, 1):
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(error.get("severity", "medium"), "⚪")
            
            formatted.append(f"\n### {severity_emoji} Error {i}: {error['type']}")
            formatted.append(f"**Message:** {error['message']}")
            if error.get("line"):
                formatted.append(f"**Line:** {error['line']}")
            if error.get("fix_suggestion"):
                formatted.append(f"**Fix:** {error['fix_suggestion']}")
        
        return "\n".join(formatted)
    
    def _smart_truncate(self, code: str, max_length: int) -> str:
        """Truncate code intelligently at line boundaries"""
        if len(code) <= max_length:
            return code
        
        lines = code.split('\n')
        truncated_lines = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) + 1 > max_length:
                break
            truncated_lines.append(line)
            current_length += len(line) + 1
        
        if truncated_lines:
            return '\n'.join(truncated_lines) + '\n# ... (truncated)'
        else:
            # If first line is too long, truncate at max_length
            return code[:max_length] + '\n# ... (truncated)'

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = CISAssistantServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
