from enum import Enum

__author__ = 'Mahmud'


class ViewActionEnum(Enum):
    Details = 'details'
    KeyInfo = 'key_information'
    Edit = 'edit'
    Delete = 'delete'
    Create = 'create'
    Restore = 'restore'
    RestoreReject = 'reject_undo'
    Manage = 'manage'
    Tree = 'tree'
    Tab = 'tab'
    Import = 'import'
    AdvancedImport = 'advanced_import'
    AdvancedExport = 'advanced_export'
    Export = 'export'
    Download = 'download'
    SecureDownload = 'secure_download'
    Reload = 'reload'
    BackUp = 'backup'
    Print = 'print'
    RunImporter = 'run_importer'
    Mutate = 'mutate'
    Approve = 'approve'
    Reject = 'reject'
    StepBack = 'step_back'
    Activate = 'activate'
    Deactivate = 'deactivate'
    ResetPassword = "reset_password"

    PartialEdit = 'partial_edit'
    PartialDelete = 'partial_delete'
    PartialCreate = 'partial_create'
    PartialFileUpload = 'partial_file_upload'

    PartialBulkAdd = 'bulk_add'
    PartialBulkRemove = 'bulk_remove'

    RouteDesign = 'route_designs'
    Version = 'version'

    ProxyLevel = 'level'
    ProxyCreate = 'proxy_create'
    ProxyDetails = 'proxy_details'

    def __str__(self):
        return self.value
