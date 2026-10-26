import { apiUrl } from '../utils/api'
import { apiDownload } from '../utils/download'

export function useExports() {
  const exportTransactionsExcel = () => apiDownload('/api/export/transactions', 'Tostiyk_Transactions.csv')
  const exportPartsExcel        = () => apiDownload('/api/export/parts', 'Tostiyk_Parts_Catalog.csv')
  const exportClientsExcel      = () => apiDownload('/api/export/clients', 'Tostiyk_Clients_Directory.csv')
  const downloadDatabaseBackup  = () => apiDownload('/api/backup/download', 'tostiyk_backup.db')
  const downloadPartsTemplate   = () => window.open(apiUrl('/api/export/template/parts'), '_blank')
  return { exportTransactionsExcel, exportPartsExcel, exportClientsExcel, downloadDatabaseBackup, downloadPartsTemplate }
}
