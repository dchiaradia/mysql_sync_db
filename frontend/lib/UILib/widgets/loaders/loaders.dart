import 'package:flutter/material.dart';

class UILibLoader extends StatelessWidget {
  final double size;
  final Color? color;

  const UILibLoader({super.key, this.size = 20, this.color});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CircularProgressIndicator(
        strokeWidth: 2,
        valueColor: AlwaysStoppedAnimation<Color>(
          color ?? Theme.of(context).primaryColor,
        ),
      ),
    );
  }
}

class UILibFullScreenLoader extends StatelessWidget {
  final String? message;

  const UILibFullScreenLoader({super.key, this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black54,
      child: Center(
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const UILibLoader(size: 40),
                if (message != null) ...[
                  const SizedBox(height: 16),
                  Text(message!, style: Theme.of(context).textTheme.bodyLarge),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
