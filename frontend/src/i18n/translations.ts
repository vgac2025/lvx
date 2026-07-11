/**
 * Traductions multilingues ARTCB Frontend
 * Langues: FR, EN, ZH, ES, PT, IT, RU
 */

export type Language = 'fr' | 'en' | 'zh' | 'es' | 'pt' | 'it' | 'ru';

export interface Translations {
  // Navigation
  nav_dashboard: string;
  nav_encode: string;
  nav_agents: string;
  nav_chain: string;
  nav_pol: string;
  
  // Dashboard
  dashboard_title: string;
  dashboard_subtitle: string;
  dashboard_blocks: string;
  dashboard_pol_score: string;
  dashboard_graphs: string;
  
  // Encode
  encode_title: string;
  encode_placeholder: string;
  encode_button: string;
  encode_success: string;
  encode_error: string;
  
  // Agents
  agents_title: string;
  agents_run: string;
  agents_explorer: string;
  agents_critic: string;
  agents_status: string;
  
  // Chain
  chain_title: string;
  chain_blocks: string;
  chain_valid: string;
  chain_invalid: string;
  chain_verify: string;
  
  // PoL
  pol_title: string;
  pol_score: string;
  pol_compression: string;
  pol_validation: string;
  pol_retrieval: string;
  
  // Common
  loading: string;
  error: string;
  success: string;
  cancel: string;
  confirm: string;
  close: string;
  save: string;
  delete: string;
  edit: string;
  view: string;
  
  // Status
  status_healthy: string;
  status_unhealthy: string;
  status_pending: string;
  status_completed: string;
  status_failed: string;
}

export const translations: Record<Language, Translations> = {
  fr: {
    // Navigation
    nav_dashboard: 'Tableau de bord',
    nav_encode: 'Encoder',
    nav_agents: 'Agents',
    nav_chain: 'Chaîne',
    nav_pol: 'PoL',
    
    // Dashboard
    dashboard_title: 'Tableau de bord ARTCB',
    dashboard_subtitle: 'Mémoire collective décentralisée',
    dashboard_blocks: 'Blocs',
    dashboard_pol_score: 'Score PoL',
    dashboard_graphs: 'Graphes',
    
    // Encode
    encode_title: 'Encoder du texte',
    encode_placeholder: 'Entrez votre texte ici...',
    encode_button: 'Encoder',
    encode_success: 'Texte encodé avec succès',
    encode_error: 'Erreur lors de l\'encodage',
    
    // Agents
    agents_title: 'Agents IA',
    agents_run: 'Exécuter',
    agents_explorer: 'Explorateur',
    agents_critic: 'Critique',
    agents_status: 'Statut',
    
    // Chain
    chain_title: 'Blockchain',
    chain_blocks: 'Blocs',
    chain_valid: 'Chaîne valide',
    chain_invalid: 'Chaîne invalide',
    chain_verify: 'Vérifier',
    
    // PoL
    pol_title: 'Preuve d\'Apprentissage',
    pol_score: 'Score',
    pol_compression: 'Compression',
    pol_validation: 'Validation',
    pol_retrieval: 'Récupération',
    
    // Common
    loading: 'Chargement...',
    error: 'Erreur',
    success: 'Succès',
    cancel: 'Annuler',
    confirm: 'Confirmer',
    close: 'Fermer',
    save: 'Enregistrer',
    delete: 'Supprimer',
    edit: 'Modifier',
    view: 'Voir',
    
    // Status
    status_healthy: 'Sain',
    status_unhealthy: 'Défaillant',
    status_pending: 'En attente',
    status_completed: 'Terminé',
    status_failed: 'Échoué',
  },
  
  en: {
    // Navigation
    nav_dashboard: 'Dashboard',
    nav_encode: 'Encode',
    nav_agents: 'Agents',
    nav_chain: 'Chain',
    nav_pol: 'PoL',
    
    // Dashboard
    dashboard_title: 'ARTCB Dashboard',
    dashboard_subtitle: 'Decentralized Collective Memory',
    dashboard_blocks: 'Blocks',
    dashboard_pol_score: 'PoL Score',
    dashboard_graphs: 'Graphs',
    
    // Encode
    encode_title: 'Encode Text',
    encode_placeholder: 'Enter your text here...',
    encode_button: 'Encode',
    encode_success: 'Text encoded successfully',
    encode_error: 'Error encoding text',
    
    // Agents
    agents_title: 'AI Agents',
    agents_run: 'Run',
    agents_explorer: 'Explorer',
    agents_critic: 'Critic',
    agents_status: 'Status',
    
    // Chain
    chain_title: 'Blockchain',
    chain_blocks: 'Blocks',
    chain_valid: 'Chain valid',
    chain_invalid: 'Chain invalid',
    chain_verify: 'Verify',
    
    // PoL
    pol_title: 'Proof of Learning',
    pol_score: 'Score',
    pol_compression: 'Compression',
    pol_validation: 'Validation',
    pol_retrieval: 'Retrieval',
    
    // Common
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    cancel: 'Cancel',
    confirm: 'Confirm',
    close: 'Close',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    view: 'View',
    
    // Status
    status_healthy: 'Healthy',
    status_unhealthy: 'Unhealthy',
    status_pending: 'Pending',
    status_completed: 'Completed',
    status_failed: 'Failed',
  },
  
  zh: {
    // Navigation
    nav_dashboard: '仪表板',
    nav_encode: '编码',
    nav_agents: '代理',
    nav_chain: '区块链',
    nav_pol: '学习证明',
    
    // Dashboard
    dashboard_title: 'ARTCB 仪表板',
    dashboard_subtitle: '去中心化集体记忆',
    dashboard_blocks: '区块',
    dashboard_pol_score: '学习证明分数',
    dashboard_graphs: '图表',
    
    // Encode
    encode_title: '编码文本',
    encode_placeholder: '在此输入您的文本...',
    encode_button: '编码',
    encode_success: '文本编码成功',
    encode_error: '编码文本时出错',
    
    // Agents
    agents_title: 'AI 代理',
    agents_run: '运行',
    agents_explorer: '探索者',
    agents_critic: '评论家',
    agents_status: '状态',
    
    // Chain
    chain_title: '区块链',
    chain_blocks: '区块',
    chain_valid: '链有效',
    chain_invalid: '链无效',
    chain_verify: '验证',
    
    // PoL
    pol_title: '学习证明',
    pol_score: '分数',
    pol_compression: '压缩',
    pol_validation: '验证',
    pol_retrieval: '检索',
    
    // Common
    loading: '加载中...',
    error: '错误',
    success: '成功',
    cancel: '取消',
    confirm: '确认',
    close: '关闭',
    save: '保存',
    delete: '删除',
    edit: '编辑',
    view: '查看',
    
    // Status
    status_healthy: '健康',
    status_unhealthy: '不健康',
    status_pending: '待处理',
    status_completed: '已完成',
    status_failed: '失败',
  },
  
  es: {
    // Navigation
    nav_dashboard: 'Panel',
    nav_encode: 'Codificar',
    nav_agents: 'Agentes',
    nav_chain: 'Cadena',
    nav_pol: 'PoL',
    
    // Dashboard
    dashboard_title: 'Panel ARTCB',
    dashboard_subtitle: 'Memoria Colectiva Descentralizada',
    dashboard_blocks: 'Bloques',
    dashboard_pol_score: 'Puntuación PoL',
    dashboard_graphs: 'Gráficos',
    
    // Encode
    encode_title: 'Codificar texto',
    encode_placeholder: 'Ingrese su texto aquí...',
    encode_button: 'Codificar',
    encode_success: 'Texto codificado exitosamente',
    encode_error: 'Error al codificar el texto',
    
    // Agents
    agents_title: 'Agentes IA',
    agents_run: 'Ejecutar',
    agents_explorer: 'Explorador',
    agents_critic: 'Crítico',
    agents_status: 'Estado',
    
    // Chain
    chain_title: 'Blockchain',
    chain_blocks: 'Bloques',
    chain_valid: 'Cadena válida',
    chain_invalid: 'Cadena inválida',
    chain_verify: 'Verificar',
    
    // PoL
    pol_title: 'Prueba de Aprendizaje',
    pol_score: 'Puntuación',
    pol_compression: 'Compresión',
    pol_validation: 'Validación',
    pol_retrieval: 'Recuperación',
    
    // Common
    loading: 'Cargando...',
    error: 'Error',
    success: 'Éxito',
    cancel: 'Cancelar',
    confirm: 'Confirmar',
    close: 'Cerrar',
    save: 'Guardar',
    delete: 'Eliminar',
    edit: 'Editar',
    view: 'Ver',
    
    // Status
    status_healthy: 'Saludable',
    status_unhealthy: 'No saludable',
    status_pending: 'Pendiente',
    status_completed: 'Completado',
    status_failed: 'Fallido',
  },
  
  pt: {
    // Navigation
    nav_dashboard: 'Painel',
    nav_encode: 'Codificar',
    nav_agents: 'Agentes',
    nav_chain: 'Cadeia',
    nav_pol: 'PoL',
    
    // Dashboard
    dashboard_title: 'Painel ARTCB',
    dashboard_subtitle: 'Memória Coletiva Descentralizada',
    dashboard_blocks: 'Blocos',
    dashboard_pol_score: 'Pontuação PoL',
    dashboard_graphs: 'Gráficos',
    
    // Encode
    encode_title: 'Codificar texto',
    encode_placeholder: 'Digite seu texto aqui...',
    encode_button: 'Codificar',
    encode_success: 'Texto codificado com sucesso',
    encode_error: 'Erro ao codificar texto',
    
    // Agents
    agents_title: 'Agentes IA',
    agents_run: 'Executar',
    agents_explorer: 'Explorador',
    agents_critic: 'Crítico',
    agents_status: 'Status',
    
    // Chain
    chain_title: 'Blockchain',
    chain_blocks: 'Blocos',
    chain_valid: 'Cadeia válida',
    chain_invalid: 'Cadeia inválida',
    chain_verify: 'Verificar',
    
    // PoL
    pol_title: 'Prova de Aprendizagem',
    pol_score: 'Pontuação',
    pol_compression: 'Compressão',
    pol_validation: 'Validação',
    pol_retrieval: 'Recuperação',
    
    // Common
    loading: 'Carregando...',
    error: 'Erro',
    success: 'Sucesso',
    cancel: 'Cancelar',
    confirm: 'Confirmar',
    close: 'Fechar',
    save: 'Salvar',
    delete: 'Excluir',
    edit: 'Editar',
    view: 'Ver',
    
    // Status
    status_healthy: 'Saudável',
    status_unhealthy: 'Não saudável',
    status_pending: 'Pendente',
    status_completed: 'Concluído',
    status_failed: 'Falhou',
  },
  
  it: {
    // Navigation
    nav_dashboard: 'Pannello',
    nav_encode: 'Codifica',
    nav_agents: 'Agenti',
    nav_chain: 'Catena',
    nav_pol: 'PoL',
    
    // Dashboard
    dashboard_title: 'Pannello ARTCB',
    dashboard_subtitle: 'Memoria Collettiva Decentralizzata',
    dashboard_blocks: 'Blocchi',
    dashboard_pol_score: 'Punteggio PoL',
    dashboard_graphs: 'Grafici',
    
    // Encode
    encode_title: 'Codifica testo',
    encode_placeholder: 'Inserisci il tuo testo qui...',
    encode_button: 'Codifica',
    encode_success: 'Testo codificato con successo',
    encode_error: 'Errore nella codifica del testo',
    
    // Agents
    agents_title: 'Agenti IA',
    agents_run: 'Esegui',
    agents_explorer: 'Esploratore',
    agents_critic: 'Critico',
    agents_status: 'Stato',
    
    // Chain
    chain_title: 'Blockchain',
    chain_blocks: 'Blocchi',
    chain_valid: 'Catena valida',
    chain_invalid: 'Catena non valida',
    chain_verify: 'Verifica',
    
    // PoL
    pol_title: 'Prova di Apprendimento',
    pol_score: 'Punteggio',
    pol_compression: 'Compressione',
    pol_validation: 'Validazione',
    pol_retrieval: 'Recupero',
    
    // Common
    loading: 'Caricamento...',
    error: 'Errore',
    success: 'Successo',
    cancel: 'Annulla',
    confirm: 'Conferma',
    close: 'Chiudi',
    save: 'Salva',
    delete: 'Elimina',
    edit: 'Modifica',
    view: 'Visualizza',
    
    // Status
    status_healthy: 'Sano',
    status_unhealthy: 'Non sano',
    status_pending: 'In attesa',
    status_completed: 'Completato',
    status_failed: 'Fallito',
  },
  
  ru: {
    // Navigation
    nav_dashboard: 'Панель',
    nav_encode: 'Кодировать',
    nav_agents: 'Агенты',
    nav_chain: 'Цепь',
    nav_pol: 'PoL',
    
    // Dashboard
    dashboard_title: 'Панель ARTCB',
    dashboard_subtitle: 'Децентрализованная коллективная память',
    dashboard_blocks: 'Блоки',
    dashboard_pol_score: 'Оценка PoL',
    dashboard_graphs: 'Графики',
    
    // Encode
    encode_title: 'Кодировать текст',
    encode_placeholder: 'Введите текст здесь...',
    encode_button: 'Кодировать',
    encode_success: 'Текст успешно закодирован',
    encode_error: 'Ошибка кодирования текста',
    
    // Agents
    agents_title: 'ИИ Агенты',
    agents_run: 'Запустить',
    agents_explorer: 'Исследователь',
    agents_critic: 'Критик',
    agents_status: 'Статус',
    
    // Chain
    chain_title: 'Блокчейн',
    chain_blocks: 'Блоки',
    chain_valid: 'Цепь действительна',
    chain_invalid: 'Цепь недействительна',
    chain_verify: 'Проверить',
    
    // PoL
    pol_title: 'Доказательство обучения',
    pol_score: 'Оценка',
    pol_compression: 'Сжатие',
    pol_validation: 'Проверка',
    pol_retrieval: 'Извлечение',
    
    // Common
    loading: 'Загрузка...',
    error: 'Ошибка',
    success: 'Успех',
    cancel: 'Отмена',
    confirm: 'Подтвердить',
    close: 'Закрыть',
    save: 'Сохранить',
    delete: 'Удалить',
    edit: 'Редактировать',
    view: 'Просмотр',
    
    // Status
    status_healthy: 'Здоров',
    status_unhealthy: 'Нездоров',
    status_pending: 'Ожидание',
    status_completed: 'Завершено',
    status_failed: 'Не удалось',
  },
};

export function getTranslation(lang: Language, key: keyof Translations): string {
  return translations[lang][key] || translations.en[key];
}

export function getCurrentLanguage(): Language {
  const stored = localStorage.getItem('artcb_language');
  if (stored && stored in translations) {
    return stored as Language;
  }
  
  const browserLang = navigator.language.split('-')[0];
  if (browserLang in translations) {
    return browserLang as Language;
  }
  
  return 'en';
}

export function setLanguage(lang: Language): void {
  localStorage.setItem('artcb_language', lang);
  window.dispatchEvent(new Event('languagechange'));
}

// Made with Bob
