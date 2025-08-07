import 'package:flutter/material.dart';
import '../models/database_models.dart';
import '../services/api_service.dart';
import '../UILib/uilib.dart';

class CronJobsDialog extends StatefulWidget {
  const CronJobsDialog({super.key});

  @override
  State<CronJobsDialog> createState() => _CronJobsDialogState();
}

class _CronJobsDialogState extends State<CronJobsDialog>
    with SingleTickerProviderStateMixin {
  final ApiService _apiService = ApiService();
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _cronExpressionController = TextEditingController();
  final _descriptionController = TextEditingController();

  List<CronJobResponse> _cronJobs = [];
  bool _isLoading = false;
  bool _isCreating = false;
  String? _error;
  bool _overwrite = false;
  int _maxTables = 1000;

  late AnimationController _animationController;
  late Animation<double> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _loadCronJobs();

    // Configuração da animação
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _slideAnimation = Tween<double>(begin: 1.0, end: 0.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );

    // Inicia a animação
    _animationController.forward();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _cronExpressionController.dispose();
    _descriptionController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _loadCronJobs() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final cronJobsList = await _apiService.listCronJobs();
      setState(() {
        _cronJobs = cronJobsList.jobs;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _createCronJob() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isCreating = true;
    });

    try {
      final jobData = CronJobCreate(
        name: _nameController.text.trim(),
        cronExpression: _cronExpressionController.text.trim(),
        description: _descriptionController.text.trim().isEmpty
            ? null
            : _descriptionController.text.trim(),
        overwrite: _overwrite,
        maxTables: _maxTables,
      );

      await _apiService.createCronJob(jobData);

      if (!mounted) return;

      // Limpar formulário
      _nameController.clear();
      _cronExpressionController.clear();
      _descriptionController.clear();
      setState(() {
        _overwrite = false;
        _maxTables = 10;
      });

      // Recarregar lista
      await _loadCronJobs();

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Cron job criado com sucesso!'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erro ao criar cron job: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isCreating = false;
        });
      }
    }
  }

  Future<void> _deleteCronJob(String jobId, String jobName) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Confirmar Exclusão'),
        content: Text('Tem certeza que deseja excluir o cron job "$jobName"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Excluir'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    try {
      await _apiService.deleteCronJob(jobId);

      if (!mounted) return;

      await _loadCronJobs();

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Cron job "$jobName" excluído com sucesso!'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erro ao excluir cron job: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  String _formatCronExpression(String expression) {
    // Exemplos de expressões cron comuns
    final examples = {
      '0 */6 * * *': 'A cada 6 horas',
      '0 0 * * *': 'Diariamente à meia-noite',
      '0 0 * * 0': 'Semanalmente no domingo',
      '0 0 1 * *': 'Mensalmente no dia 1',
      '0 0 1 1 *': 'Anualmente no dia 1 de janeiro',
      '*/15 * * * *': 'A cada 15 minutos',
      '0 */2 * * *': 'A cada 2 horas',
    };

    return examples[expression] ?? expression;
  }

  String _formatDateTime(DateTime? dateTime) {
    if (dateTime == null) return 'Nunca';
    return '${dateTime.day.toString().padLeft(2, '0')}/${dateTime.month.toString().padLeft(2, '0')}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  Color _getStatusColor(CronJobStatus status) {
    switch (status) {
      case CronJobStatus.active:
        return Colors.green;
      case CronJobStatus.paused:
        return Colors.orange;
      case CronJobStatus.removed:
        return Colors.red;
    }
  }

  void _closeDialog() async {
    await _animationController.reverse();
    if (mounted) {
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return Stack(
          children: [
            // Overlay escuro
            Positioned.fill(
              child: GestureDetector(
                onTap: _closeDialog,
                child: Container(
                  color: Colors.black.withOpacity(0.5 * _slideAnimation.value),
                ),
              ),
            ),
            // SideDialog
            Positioned(
              right: 0,
              top: 0,
              bottom: 0,
              width: MediaQuery.of(context).size.width * 0.6,
              child: Transform.translate(
                offset: Offset(
                  MediaQuery.of(context).size.width *
                      0.4 *
                      _slideAnimation.value,
                  0,
                ),
                child: Container(
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black26,
                        blurRadius: 10,
                        offset: Offset(-2, 0),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      // Header
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.blue,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black12,
                              blurRadius: 4,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.schedule,
                              size: 24,
                              color: Colors.white,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'Gerenciar Cron Jobs',
                                style: Theme.of(context).textTheme.headlineSmall
                                    ?.copyWith(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                            ),
                            IconButton(
                              onPressed: _closeDialog,
                              icon: const Icon(
                                Icons.close,
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ),

                      // Content
                      Expanded(
                        child: SingleChildScrollView(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Form Section
                              Card(
                                elevation: 4,
                                child: Padding(
                                  padding: const EdgeInsets.all(16),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Criar Novo Cron Job',
                                        style: Theme.of(context)
                                            .textTheme
                                            .titleMedium
                                            ?.copyWith(
                                              fontWeight: FontWeight.bold,
                                            ),
                                      ),
                                      const SizedBox(height: 16),
                                      Form(
                                        key: _formKey,
                                        child: Column(
                                          children: [
                                            TextFormField(
                                              controller: _nameController,
                                              decoration: const InputDecoration(
                                                labelText: 'Nome do Job',
                                                border: OutlineInputBorder(),
                                              ),
                                              validator: (value) {
                                                if (value == null ||
                                                    value.trim().isEmpty) {
                                                  return 'Nome é obrigatório';
                                                }
                                                return null;
                                              },
                                            ),
                                            const SizedBox(height: 16),
                                            TextFormField(
                                              controller:
                                                  _cronExpressionController,
                                              decoration: const InputDecoration(
                                                labelText: 'Expressão Cron',
                                                border: OutlineInputBorder(),
                                                helperText:
                                                    'Ex: 0 */6 * * * (a cada 6 horas)',
                                              ),
                                              validator: (value) {
                                                if (value == null ||
                                                    value.trim().isEmpty) {
                                                  return 'Expressão cron é obrigatória';
                                                }
                                                return null;
                                              },
                                            ),
                                            const SizedBox(height: 16),
                                            TextFormField(
                                              controller:
                                                  _descriptionController,
                                              decoration: const InputDecoration(
                                                labelText:
                                                    'Descrição (opcional)',
                                                border: OutlineInputBorder(),
                                              ),
                                              maxLines: 3,
                                            ),
                                            const SizedBox(height: 16),
                                            Row(
                                              children: [
                                                Expanded(
                                                  child: CheckboxListTile(
                                                    title: const Text(
                                                      'Sobrescrever tabelas',
                                                    ),
                                                    value: _overwrite,
                                                    onChanged: (value) {
                                                      setState(() {
                                                        _overwrite =
                                                            value ?? false;
                                                      });
                                                    },
                                                  ),
                                                ),
                                              ],
                                            ),
                                            const SizedBox(height: 16),
                                            Row(
                                              children: [
                                                const Text('Máx. tabelas: '),
                                                Expanded(
                                                  child: Slider(
                                                    value: _maxTables
                                                        .toDouble(),
                                                    min: 1,
                                                    max: 1000,
                                                    divisions: 10,
                                                    label: _maxTables
                                                        .toString(),
                                                    onChanged: (value) {
                                                      setState(() {
                                                        _maxTables = value
                                                            .round();
                                                      });
                                                    },
                                                  ),
                                                ),
                                                Text(_maxTables.toString()),
                                              ],
                                            ),
                                            const SizedBox(height: 16),
                                            UILibButton.primary(
                                              label: _isCreating
                                                  ? 'Criando...'
                                                  : 'Criar Cron Job',
                                              onPressed: _isCreating
                                                  ? null
                                                  : _createCronJob,
                                              loading: _isCreating,
                                              fullWidth: true,
                                              icon: _isCreating
                                                  ? null
                                                  : Icons.add,
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),

                              const SizedBox(height: 24),

                              // List Section
                              Card(
                                elevation: 4,
                                child: Padding(
                                  padding: const EdgeInsets.all(16),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: [
                                          Text(
                                            'Cron Jobs Existentes',
                                            style: Theme.of(context)
                                                .textTheme
                                                .titleMedium
                                                ?.copyWith(
                                                  fontWeight: FontWeight.bold,
                                                ),
                                          ),
                                          const Spacer(),
                                          IconButton(
                                            onPressed: _loadCronJobs,
                                            icon: const Icon(Icons.refresh),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 16),
                                      _isLoading
                                          ? const Center(
                                              child:
                                                  CircularProgressIndicator(),
                                            )
                                          : _error != null
                                          ? Center(
                                              child: Column(
                                                mainAxisAlignment:
                                                    MainAxisAlignment.center,
                                                children: [
                                                  const Icon(
                                                    Icons.error,
                                                    size: 48,
                                                    color: Colors.red,
                                                  ),
                                                  const SizedBox(height: 8),
                                                  Text(_error!),
                                                  const SizedBox(height: 16),
                                                  UILibButton.primary(
                                                    label: 'Tentar Novamente',
                                                    onPressed: _loadCronJobs,
                                                  ),
                                                ],
                                              ),
                                            )
                                          : _cronJobs.isEmpty
                                          ? const Center(
                                              child: Padding(
                                                padding: EdgeInsets.all(32.0),
                                                child: Text(
                                                  'Nenhum cron job cadastrado',
                                                ),
                                              ),
                                            )
                                          : Column(
                                              children: _cronJobs.map((job) {
                                                return Card(
                                                  margin: const EdgeInsets.only(
                                                    bottom: 8,
                                                  ),
                                                  elevation: 2,
                                                  child: ListTile(
                                                    title: Text(
                                                      job.name,
                                                      style: const TextStyle(
                                                        fontWeight:
                                                            FontWeight.bold,
                                                      ),
                                                    ),
                                                    subtitle: Column(
                                                      crossAxisAlignment:
                                                          CrossAxisAlignment
                                                              .start,
                                                      children: [
                                                        if (job.description !=
                                                            null)
                                                          Text(
                                                            job.description!,
                                                          ),
                                                        Text(
                                                          'Cron: ${_formatCronExpression(job.cronExpression)}',
                                                        ),
                                                        Text(
                                                          'Próxima execução: ${_formatDateTime(job.nextRun)}',
                                                        ),
                                                        if (job.lastRun != null)
                                                          Text(
                                                            'Última execução: ${_formatDateTime(job.lastRun)}',
                                                          ),
                                                        Text(
                                                          'Config: ${job.maxTables} tabelas, ${job.overwrite ? "sobrescrever" : "não sobrescrever"}',
                                                        ),
                                                      ],
                                                    ),
                                                    trailing: Row(
                                                      mainAxisSize:
                                                          MainAxisSize.min,
                                                      children: [
                                                        Container(
                                                          padding:
                                                              const EdgeInsets.symmetric(
                                                                horizontal: 8,
                                                                vertical: 4,
                                                              ),
                                                          decoration: BoxDecoration(
                                                            color:
                                                                _getStatusColor(
                                                                  job.status,
                                                                ),
                                                            borderRadius:
                                                                BorderRadius.circular(
                                                                  12,
                                                                ),
                                                          ),
                                                          child: Text(
                                                            job.status
                                                                .toString()
                                                                .split('.')
                                                                .last
                                                                .toUpperCase(),
                                                            style:
                                                                const TextStyle(
                                                                  color: Colors
                                                                      .white,
                                                                  fontSize: 12,
                                                                  fontWeight:
                                                                      FontWeight
                                                                          .bold,
                                                                ),
                                                          ),
                                                        ),
                                                        const SizedBox(
                                                          width: 8,
                                                        ),
                                                        IconButton(
                                                          onPressed: () =>
                                                              _deleteCronJob(
                                                                job.id,
                                                                job.name,
                                                              ),
                                                          icon: const Icon(
                                                            Icons.delete,
                                                            color: Colors.red,
                                                          ),
                                                          tooltip: 'Excluir',
                                                        ),
                                                      ],
                                                    ),
                                                    isThreeLine: true,
                                                  ),
                                                );
                                              }).toList(),
                                            ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}
