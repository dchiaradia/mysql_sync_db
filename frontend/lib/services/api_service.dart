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
      final response = await http.get(Uri.parse('$baseUrl/health'));

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
          '$baseUrl/source/tables?sort_by_dependencies=$sortByDependencies',
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
          '$baseUrl/destination/tables?sort_by_dependencies=$sortByDependencies',
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
        Uri.parse('$baseUrl/migrate/$tableName?overwrite=$overwrite'),
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
          '$baseUrl/migrate-batch?max_tables=$maxTables&overwrite=$overwrite',
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
}
