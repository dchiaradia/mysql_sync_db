import 'package:flutter/material.dart';

enum UILibButtonType { primary, secondary, text }

class UILibButton extends StatelessWidget {
  final String? label;
  final VoidCallback? onPressed;
  final UILibButtonType type;
  final bool loading;
  final bool fullWidth;
  final IconData? icon;

  const UILibButton({
    super.key,
    this.label,
    this.onPressed,
    this.type = UILibButtonType.primary,
    this.loading = false,
    this.fullWidth = false,
    this.icon,
  });

  const UILibButton.primary({
    super.key,
    required this.label,
    this.onPressed,
    this.loading = false,
    this.fullWidth = false,
    this.icon,
  }) : type = UILibButtonType.primary;

  const UILibButton.secondary({
    super.key,
    required this.label,
    this.onPressed,
    this.loading = false,
    this.fullWidth = false,
    this.icon,
  }) : type = UILibButtonType.secondary;

  const UILibButton.text({
    super.key,
    required this.label,
    this.onPressed,
    this.loading = false,
    this.fullWidth = false,
    this.icon,
  }) : type = UILibButtonType.text;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 48,
      width: fullWidth ? double.infinity : null,
      child: _buildButton(),
    );
  }

  Widget _buildButton() {
    if (loading) {
      return ElevatedButton(
        onPressed: null,
        style: _getButtonStyle(),
        child: const SizedBox(
          width: 20,
          height: 20,
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      );
    }

    switch (type) {
      case UILibButtonType.primary:
        return ElevatedButton(
          onPressed: onPressed,
          style: _getButtonStyle(),
          child: _buildContent(),
        );
      case UILibButtonType.secondary:
        return OutlinedButton(
          onPressed: onPressed,
          style: _getButtonStyle(),
          child: _buildContent(),
        );
      case UILibButtonType.text:
        return TextButton(
          onPressed: onPressed,
          style: _getButtonStyle(),
          child: _buildContent(),
        );
    }
  }

  Widget _buildContent() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (icon != null) ...[Icon(icon, size: 20), const SizedBox(width: 8)],
        if (label != null) Text(label!),
      ],
    );
  }

  ButtonStyle _getButtonStyle() {
    switch (type) {
      case UILibButtonType.primary:
        return ElevatedButton.styleFrom(
          backgroundColor: Colors.grey[900],
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        );
      case UILibButtonType.secondary:
        return OutlinedButton.styleFrom(
          foregroundColor: Colors.blue,
          side: const BorderSide(color: Colors.blue),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        );
      case UILibButtonType.text:
        return TextButton.styleFrom(
          foregroundColor: Colors.blue,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        );
    }
  }
}
