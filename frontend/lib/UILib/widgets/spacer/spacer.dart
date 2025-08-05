import 'package:flutter/material.dart';

class UILibSpacer extends StatelessWidget {
  final double height;
  final double width;

  const UILibSpacer({super.key, this.height = 0, this.width = 0});

  const UILibSpacer.vertical({super.key, this.height = 16}) : width = 0;
  const UILibSpacer.horizontal({super.key, this.width = 16}) : height = 0;

  @override
  Widget build(BuildContext context) {
    return SizedBox(height: height, width: width);
  }
}
