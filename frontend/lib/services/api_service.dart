import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/database_models.dart';
import '../config/env_config.dart';

class ApiService {
  static const String baseUrl = EnvConfig.apiBaseUrl;

  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  Future<HealthCheck> getHealth() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/database/health'));

      if (response.statusCode == 200) {
        return HealthCheck.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to get health status: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error connecting to API: $e');
    }
  }

  Future<DatabaseSummary> getSourceTables({
    bool sortByDependencies = false,
  }) async {
    try {
      final response = await http.get(
        Uri.parse(
          '$baseUrl/database/source/tables?sort_by_dependencies=$sortByDependencies',
        ),
      );

      if (response.statusCode == 200) {
        return DatabaseSummary.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to get source tables: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error getting source tables: $e');
    }
  }

  Future<DatabaseSummary> getDestinationTables({
    bool sortByDependencies = false,
  }) async {
    try {
      final response = await http.get(
        Uri.parse(
          '$baseUrl/database/destination/tables?sort_by_dependencies=$sortByDependencies',
        ),
      );

      if (response.statusCode == 200) {
        return DatabaseSummary.fromJson(json.decode(response.body));
      } else {
        throw Exception(
          'Failed to get destination tables: ${response.statusCode}',
        );
      }
    } catch (e) {
      throw Exception('Error getting destination tables: $e');
    }
  }

  Future<MigrationResult> migrateTable(
    String tableName, {
    bool overwrite = true,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/database/migrate/$tableName?overwrite=$overwrite'),
      );

      if (response.statusCode == 200) {
        return MigrationResult.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to migrate table: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error migrating table: $e');
    }
  }

  Future<BatchMigrationResult> migrateBatch({
    int maxTables = 10,
    bool overwrite = true,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(
          '$baseUrl/database/migrate-batch?max_tables=$maxTables&overwrite=$overwrite',
        ),
      );

      if (response.statusCode == 200) {
        return BatchMigrationResult.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to migrate batch: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error migrating batch: $e');
    }
  }

  // Cron Job Methods
  Future<CronJobResponse> createCronJob(CronJobCreate jobData) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/cron/jobs'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(jobData.toJson()),
      );

      if (response.statusCode == 201) {
        return CronJobResponse.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to create cron job: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error creating cron job: $e');
    }
  }

  Future<CronJobList> listCronJobs() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/cron/jobs'));

      if (response.statusCode == 200) {
        return CronJobList.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to list cron jobs: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error listing cron jobs: $e');
    }
  }

  Future<CronJobDelete> deleteCronJob(String jobId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/cron/jobs/$jobId'),
      );

      if (response.statusCode == 200) {
        return CronJobDelete.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to delete cron job: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error deleting cron job: $e');
    }
  }

  Future<int> getCronJobCount() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/cron/jobs/count'));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['total_jobs'] ?? 0;
      } else {
        throw Exception('Failed to get cron job count: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error getting cron job count: $e');
    }
  }
}
