import 'package:database_sync_frontend/config/env_config.dart';
import 'package:flutter/material.dart';
import '../models/database_models.dart';
import '../services/api_service.dart';
import '../UILib/uilib.dart';

class DatabaseSyncScreen extends StatefulWidget {
  const DatabaseSyncScreen({super.key});

  @override
  State<DatabaseSyncScreen> createState() => _DatabaseSyncScreenState();
}

class _DatabaseSyncScreenState extends State<DatabaseSyncScreen> {
  final ApiService _apiService = ApiService();

  DatabaseSummary? _sourceSummary;
  DatabaseSummary? _destinationSummary;
  bool _isLoading = false;
  bool _isBatchLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final sourceTables = await _apiService.getSourceTables(
        sortByDependencies: true,
      );
      final destinationTables = await _apiService.getDestinationTables();

      setState(() {
        _sourceSummary = sourceTables;
        _destinationSummary = destinationTables;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _migrateTable(String tableName) async {
    try {
      final result = await _apiService.migrateTable(tableName, overwrite: true);

      if (!mounted) return;

      if (result.success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Tabela $tableName migrada com sucesso! ${result.recordsMigrated} registros.',
            ),
            backgroundColor: Colors.green,
          ),
        );
        _loadData(); // Recarrega os dados
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erro ao migrar tabela $tableName: ${result.error}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erro ao migrar tabela: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _migrateBatch() async {
    setState(() {
      _isBatchLoading = true;
    });

    try {
      final result = await _apiService.migrateBatch(
        maxTables: _sourceSummary?.tables.length ?? 10,
        overwrite: true,
      );

      if (!mounted) return;

      setState(() {
        _isBatchLoading = false;
      });

      if (result.success) {
        _showBatchResultDialog(result);
        _loadData(); // Recarrega os dados
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Erro na migração em lote'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _isBatchLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erro na migração em lote: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _showBatchResultDialog(BatchMigrationResult result) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Resultado da Migração em Lote'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Total de tabelas: ${result.totalTables}'),
              Text('Tabelas migradas: ${result.migratedCount}'),
              const SizedBox(height: 16),
              const Text(
                'Detalhes:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              ...result.results.map(
                (r) => Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    '${r.tableName}: ${r.success ? "✅" : "❌"} ${r.recordsMigrated} registros',
                    style: TextStyle(
                      color: r.success ? Colors.green : Colors.red,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(EnvConfig.appTitle),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? _buildErrorWidget()
          : _buildContent(),
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error, size: 64, color: Colors.red),
          const UILibSpacer.vertical(height: 16),
          Text(
            'Erro ao carregar dados',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const UILibSpacer.vertical(height: 8),
          Text(_error!, style: Theme.of(context).textTheme.bodyMedium),
          const UILibSpacer.vertical(height: 16),
          UILibButton.primary(label: 'Tentar Novamente', onPressed: _loadData),
        ],
      ),
    );
  }

  Widget _buildContent() {
    if (_sourceSummary == null || _destinationSummary == null) {
      return const Center(child: Text('Nenhum dado disponível'));
    }

    return Column(
      children: [
        _buildSummaryCards(),
        const SizedBox(height: 16),
        Expanded(child: _buildTablesList()),
        _buildBatchButton(),
      ],
    );
  }

  Widget _buildSummaryCards() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(child: _buildSummaryCard('Origem', _sourceSummary!)),
          const UILibSpacer.horizontal(width: 16),
          Expanded(child: _buildSummaryCard('Destino', _destinationSummary!)),
        ],
      ),
    );
  }

  Widget _buildSummaryCard(String title, DatabaseSummary summary) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const UILibSpacer.vertical(height: 8),
            Text('Tabelas: ${summary.totalTables}'),
            Text('Registros: ${summary.totalRows}'),
            Text('Tamanho: ${summary.totalSizeMb.toStringAsFixed(2)} MB'),
          ],
        ),
      ),
    );
  }

  Widget _buildTablesList() {
    final sourceTables = _sourceSummary!.tables;
    final destinationTables = _destinationSummary!.tables;

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: sourceTables.length,
      itemBuilder: (context, index) {
        final sourceTable = sourceTables[index];
        final destinationTable = destinationTables.firstWhere(
          (table) => table.tableName == sourceTable.tableName,
          orElse: () => TableInfo(
            tableName: sourceTable.tableName,
            rowCount: 0,
            sizeMb: 0,
            dataLength: 0,
            indexLength: 0,
          ),
        );

        // Verifica se há divergência na quantidade de registros
        final hasDivergence = sourceTable.rowCount != destinationTable.rowCount;

        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          color: hasDivergence ? Colors.red.shade50 : null,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  flex: 2,
                  child: _buildTableInfo('Origem', sourceTable),
                ),
                const UILibSpacer.horizontal(width: 16),
                Expanded(
                  flex: 2,
                  child: _buildTableInfo('Destino', destinationTable),
                ),
                const UILibSpacer.horizontal(width: 16),
                UILibButton.primary(
                  label: null,
                  onPressed: _isBatchLoading
                      ? null
                      : () => _migrateTable(sourceTable.tableName),
                  icon: Icons.play_arrow,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTableInfo(String title, TableInfo table) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "$title: ${table.tableName}",
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        Text('${table.rowCount} registros'),
        Text('${table.sizeMb.toStringAsFixed(2)} MB'),
      ],
    );
  }

  Widget _buildBatchButton() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: UILibButton.primary(
        label: _isBatchLoading ? 'Migrando...' : 'Sincronizar Todas as Tabelas',
        onPressed: _isBatchLoading ? null : _migrateBatch,
        loading: _isBatchLoading,
        fullWidth: true,
        icon: _isBatchLoading ? null : Icons.play_arrow,
      ),
    );
  }
}
