import 'package:flutter/material.dart';
import 'screens/database_sync_screen.dart';
import 'config/env_config.dart';

void main() {
  runApp(const DatabaseSyncApp());
}

class DatabaseSyncApp extends StatelessWidget {
  const DatabaseSyncApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: EnvConfig.appTitle,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const DatabaseSyncScreen(),
    );
  }
}
