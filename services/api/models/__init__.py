"""Modular API schemas package."""

from __future__ import annotations

from services.api.models.accounts import AccountResponse
from services.api.models.audit import AuditEventResponse
from services.api.models.auth import LoginRequest, RefreshRequest, TokenResponse
from services.api.models.base import ApiModel, ApiResponse, PaginationMeta
from services.api.models.capabilities import PlatformCapabilityResponse
from services.api.models.communities import CommunityClusterResponse
from services.api.models.content import ContentResponse
from services.api.models.errors import ErrorDetail, ErrorResponse
from services.api.models.export import ExportRequest
from services.api.models.features import AccountFeatureResponse
from services.api.models.filters import AccountFilterParams
from services.api.models.health import HealthStatusResponse
from services.api.models.imports import DatasetImportRequest, DatasetImportResponse
from services.api.models.metrics import ServiceMetricsResponse
from services.api.models.networks import GraphEdge, GraphNode, NetworkGraphResponse
from services.api.models.pagination import PaginationQueryParams
from services.api.models.platforms import PlatformMetadata
from services.api.models.quarantine import QuarantineItemResponse
from services.api.models.relationships import RelationshipEdgeResponse
from services.api.models.reports import InvestigationReportResponse
from services.api.models.scans import CreateScanRequest, ScanResponse
from services.api.models.tokens import JwtTokenClaims
from services.api.models.users import RoleUpdateRequest, UserCreateRequest, UserResponse
from services.api.models.webhooks import WebhookPayload

__all__ = [
    "AccountFeatureResponse",
    "AccountFilterParams",
    "AccountResponse",
    "ApiModel",
    "ApiResponse",
    "AuditEventResponse",
    "CommunityClusterResponse",
    "ContentResponse",
    "CreateScanRequest",
    "DatasetImportRequest",
    "DatasetImportResponse",
    "ErrorDetail",
    "ErrorResponse",
    "ExportRequest",
    "GraphEdge",
    "GraphNode",
    "HealthStatusResponse",
    "InvestigationReportResponse",
    "JwtTokenClaims",
    "LoginRequest",
    "NetworkGraphResponse",
    "PaginationMeta",
    "PaginationQueryParams",
    "PlatformCapabilityResponse",
    "PlatformMetadata",
    "QuarantineItemResponse",
    "RefreshRequest",
    "RelationshipEdgeResponse",
    "RoleUpdateRequest",
    "ScanResponse",
    "ServiceMetricsResponse",
    "TokenResponse",
    "UserCreateRequest",
    "UserResponse",
    "WebhookPayload",
]
