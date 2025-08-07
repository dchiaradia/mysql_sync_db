class TableInfo {
  final String tableName;
  final int rowCount;
  final double sizeMb;
  final int dataLength;
  final int indexLength;

  TableInfo({
    required this.tableName,
    required this.rowCount,
    required this.sizeMb,
    required this.dataLength,
    required this.indexLength,
  });

  factory TableInfo.fromJson(Map<String, dynamic> json) {
    return TableInfo(
      tableName: json['table_name'] ?? '',
      rowCount: json['row_count'] ?? 0,
      sizeMb: (json['size_mb'] ?? 0.0).toDouble(),
      dataLength: json['data_length'] ?? 0,
      indexLength: json['index_length'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'table_name': tableName,
      'row_count': rowCount,
      'size_mb': sizeMb,
      'data_length': dataLength,
      'index_length': indexLength,
    };
  }
}

class DatabaseSummary {
  final String databaseType;
  final String databaseName;
  final int totalTables;
  final int totalRows;
  final double totalSizeMb;
  final List<TableInfo> tables;

  DatabaseSummary({
    required this.databaseType,
    required this.databaseName,
    required this.totalTables,
    required this.totalRows,
    required this.totalSizeMb,
    required this.tables,
  });

  factory DatabaseSummary.fromJson(Map<String, dynamic> json) {
    return DatabaseSummary(
      databaseType: json['database_type'] ?? '',
      databaseName: json['database_name'] ?? '',
      totalTables: json['total_tables'] ?? 0,
      totalRows: json['total_rows'] ?? 0,
      totalSizeMb: (json['total_size_mb'] ?? 0.0).toDouble(),
      tables:
          (json['tables'] as List<dynamic>?)
              ?.map((table) => TableInfo.fromJson(table))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'database_type': databaseType,
      'database_name': databaseName,
      'total_tables': totalTables,
      'total_rows': totalRows,
      'total_size_mb': totalSizeMb,
      'tables': tables.map((table) => table.toJson()).toList(),
    };
  }
}

class MigrationResult {
  final bool success;
  final String tableName;
  final int recordsMigrated;
  final bool overwritten;
  final String? error;
  final String message;

  MigrationResult({
    required this.success,
    required this.tableName,
    required this.recordsMigrated,
    required this.overwritten,
    this.error,
    required this.message,
  });

  factory MigrationResult.fromJson(Map<String, dynamic> json) {
    return MigrationResult(
      success: json['success'] ?? false,
      tableName: json['table_name'] ?? '',
      recordsMigrated: json['records_migrated'] ?? 0,
      overwritten: json['overwritten'] ?? false,
      error: json['error'],
      message: json['message'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'table_name': tableName,
      'records_migrated': recordsMigrated,
      'overwritten': overwritten,
      'error': error,
      'message': message,
    };
  }
}

class BatchMigrationResult {
  final bool success;
  final int totalTables;
  final int migratedCount;
  final int maxTables;
  final List<MigrationResult> results;
  final String message;

  BatchMigrationResult({
    required this.success,
    required this.totalTables,
    required this.migratedCount,
    required this.maxTables,
    required this.results,
    required this.message,
  });

  factory BatchMigrationResult.fromJson(Map<String, dynamic> json) {
    return BatchMigrationResult(
      success: json['success'] ?? false,
      totalTables: json['total_tables'] ?? 0,
      migratedCount: json['migrated_count'] ?? 0,
      maxTables: json['max_tables'] ?? 0,
      results:
          (json['results'] as List<dynamic>?)
              ?.map((result) => MigrationResult.fromJson(result))
              .toList() ??
          [],
      message: json['message'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'total_tables': totalTables,
      'migrated_count': migratedCount,
      'max_tables': maxTables,
      'results': results.map((result) => result.toJson()).toList(),
      'message': message,
    };
  }
}

class ConnectionStatus {
  final bool source;
  final bool destination;

  ConnectionStatus({required this.source, required this.destination});

  factory ConnectionStatus.fromJson(Map<String, dynamic> json) {
    return ConnectionStatus(
      source: json['source'] ?? false,
      destination: json['destination'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {'source': source, 'destination': destination};
  }
}

class HealthCheck {
  final String status;
  final ConnectionStatus connections;
  final String version;

  HealthCheck({
    required this.status,
    required this.connections,
    required this.version,
  });

  factory HealthCheck.fromJson(Map<String, dynamic> json) {
    return HealthCheck(
      status: json['status'] ?? '',
      connections: ConnectionStatus.fromJson(json['connections'] ?? {}),
      version: json['version'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'status': status,
      'connections': connections.toJson(),
      'version': version,
    };
  }
}

// Cron Job Models
enum CronJobStatus { active, paused, removed }

class CronJobCreate {
  final String name;
  final String cronExpression;
  final String? description;
  final bool overwrite;
  final int maxTables;

  CronJobCreate({
    required this.name,
    required this.cronExpression,
    this.description,
    this.overwrite = false,
    this.maxTables = 10,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'cron_expression': cronExpression,
      'description': description,
      'overwrite': overwrite,
      'max_tables': maxTables,
    };
  }
}

class CronJobResponse {
  final String id;
  final String name;
  final String cronExpression;
  final String? description;
  final CronJobStatus status;
  final DateTime? nextRun;
  final DateTime createdAt;
  final DateTime? lastRun;
  final bool overwrite;
  final int maxTables;

  CronJobResponse({
    required this.id,
    required this.name,
    required this.cronExpression,
    this.description,
    required this.status,
    this.nextRun,
    required this.createdAt,
    this.lastRun,
    required this.overwrite,
    required this.maxTables,
  });

  factory CronJobResponse.fromJson(Map<String, dynamic> json) {
    return CronJobResponse(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      cronExpression: json['cron_expression'] ?? '',
      description: json['description'],
      status: CronJobStatus.values.firstWhere(
        (e) => e.toString().split('.').last == json['status'],
        orElse: () => CronJobStatus.active,
      ),
      nextRun: json['next_run'] != null
          ? DateTime.parse(json['next_run'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
      lastRun: json['last_run'] != null
          ? DateTime.parse(json['last_run'])
          : null,
      overwrite: json['overwrite'] ?? false,
      maxTables: json['max_tables'] ?? 10,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'cron_expression': cronExpression,
      'description': description,
      'status': status.toString().split('.').last,
      'next_run': nextRun?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'last_run': lastRun?.toIso8601String(),
      'overwrite': overwrite,
      'max_tables': maxTables,
    };
  }
}

class CronJobList {
  final List<CronJobResponse> jobs;
  final int total;

  CronJobList({required this.jobs, required this.total});

  factory CronJobList.fromJson(Map<String, dynamic> json) {
    return CronJobList(
      jobs:
          (json['jobs'] as List<dynamic>?)
              ?.map((job) => CronJobResponse.fromJson(job))
              .toList() ??
          [],
      total: json['total'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {'jobs': jobs.map((job) => job.toJson()).toList(), 'total': total};
  }
}

class CronJobDelete {
  final bool success;
  final String message;

  CronJobDelete({required this.success, required this.message});

  factory CronJobDelete.fromJson(Map<String, dynamic> json) {
    return CronJobDelete(
      success: json['success'] ?? false,
      message: json['message'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {'success': success, 'message': message};
  }
}
