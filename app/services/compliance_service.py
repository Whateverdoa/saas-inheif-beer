"""Service for managing legal documents and compliance."""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger("uvicorn.error")

# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "legal"

# Legal document mappings
LEGAL_DOCUMENTS = {
    "terms": "terms_of_service.md",
    "privacy": "privacy_policy.md",
    "dpa": "dpa.md",
    "cookies": "cookie_policy.md",
}


class ComplianceService:
    """Service for managing legal documents and compliance tracking."""

    def __init__(self):
        self._document_cache: Dict[str, str] = {}
        self._last_updated = datetime.now()

    def _get_company_info(self) -> Dict[str, str]:
        """Get company information from environment variables."""
        return {
            "company_name": os.getenv("COMPANY_NAME", "Your Company Name"),
            "company_email": os.getenv("COMPANY_EMAIL", "contact@example.com"),
            "company_address": os.getenv("COMPANY_ADDRESS", ""),
            "kvk_number": os.getenv("COMPANY_KVK_NUMBER", ""),
            "btw_number": os.getenv("COMPANY_BTW_NUMBER", ""),
            "last_updated": self._last_updated.strftime("%Y-%m-%d"),
        }

    def _load_template(self, document_type: str) -> str:
        """Load a legal document template."""
        if document_type not in LEGAL_DOCUMENTS:
            raise ValueError(f"Unknown document type: {document_type}")

        # Check cache first
        if document_type in self._document_cache:
            return self._document_cache[document_type]

        template_file = TEMPLATE_DIR / LEGAL_DOCUMENTS[document_type]
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")

        with open(template_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Cache the template
        self._document_cache[document_type] = content
        return content

    def _render_template(self, template_content: str, context: Dict[str, str]) -> str:
        """Render template with context variables."""
        rendered = template_content
        for key, value in context.items():
            rendered = rendered.replace(f"{{{{ {key} }}}}", str(value))
        return rendered

    def get_legal_document(
        self, document_type: str, format: str = "markdown"
    ) -> Dict[str, str]:
        """
        Get a legal document by type.

        Args:
            document_type: Type of document (terms, privacy, dpa, cookies)
            format: Output format (markdown or html)

        Returns:
            Dictionary with document content and metadata
        """
        if document_type not in LEGAL_DOCUMENTS:
            raise ValueError(f"Unknown document type: {document_type}")

        template_content = self._load_template(document_type)
        context = self._get_company_info()
        rendered_content = self._render_template(template_content, context)

        if format == "html":
            # Convert markdown to HTML (simple conversion, can be enhanced with markdown library)
            rendered_content = self._markdown_to_html(rendered_content)

        return {
            "document_type": document_type,
            "content": rendered_content,
            "format": format,
            "last_updated": context["last_updated"],
            "version": "1.0",
        }

    def _markdown_to_html(self, markdown: str) -> str:
        """Simple markdown to HTML conversion."""
        # Basic conversion - can be enhanced with markdown library
        html = markdown.replace("\n\n", "</p><p>")
        html = html.replace("\n", "<br>")
        html = html.replace("# ", "<h1>").replace("\n", "</h1>", 1)
        html = html.replace("## ", "<h2>").replace("\n", "</h2>", 1)
        html = html.replace("### ", "<h3>").replace("\n", "</h3>", 1)
        html = f"<p>{html}</p>"
        return html

    def list_legal_documents(self) -> list[Dict[str, str]]:
        """List all available legal documents."""
        documents = []
        for doc_type in LEGAL_DOCUMENTS.keys():
            try:
                doc_info = self.get_legal_document(doc_type)
                documents.append({
                    "document_type": doc_type,
                    "version": doc_info["version"],
                    "last_updated": doc_info["last_updated"],
                })
            except Exception as e:
                logger.warning(f"Failed to load document {doc_type}: {e}")
        return documents


# Singleton instance
_compliance_service: Optional[ComplianceService] = None


def get_compliance_service() -> ComplianceService:
    """Get the compliance service singleton."""
    global _compliance_service
    if _compliance_service is None:
        _compliance_service = ComplianceService()
    return _compliance_service

