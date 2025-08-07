class EnvConfig {
  // API Configuration
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );

  // App Configuration
  static const String appTitle = String.fromEnvironment(
    'APP_TITLE',
    defaultValue: 'Database Sync',
  );

  // Development Configuration
  static const bool isDevelopment = bool.fromEnvironment(
    'IS_DEVELOPMENT',
    defaultValue: false,
  );

  // Debug Configuration
  static const bool enableDebug = bool.fromEnvironment(
    'ENABLE_DEBUG',
    defaultValue: false,
  );
}
