/**
 * TODO アプリ メイン
 */
import Alpine from 'alpinejs';

interface Todo {
  id: string;
  userId: string;
  title: string;
  description: string;
  dueDate: string | null;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

interface Stats {
  total: number;
  completed: number;
  active: number;
  overdue: number;
}

Alpine.data('todoApp', () => ({
  todos: [] as Todo[],
  stats: { total: 0, completed: 0, active: 0, overdue: 0 } as Stats,
  filter: '',
  showDialog: false,
  newTodo: {
    title: '',
    description: '',
    dueDate: '',
  },

  async init() {
    await this.loadTodos();
    await this.loadStats();
  },

  async loadTodos() {
    const params = new URLSearchParams();
    if (this.filter === 'active') params.append('completed', 'false');
    if (this.filter === 'completed') params.append('completed', 'true');
    
    const response = await fetch(`/api/todo-app/todos?${params.toString()}`, {
      credentials: 'include',
    });
    
    if (response.ok) {
      const data = await response.json();
      this.todos = data.todos;
    }
  },

  async loadStats() {
    const response = await fetch('/api/todo-app/todos/stats', {
      credentials: 'include',
    });
    
    if (response.ok) {
      this.stats = await response.json();
    }
  },

  showAddDialog() {
    this.newTodo = { title: '', description: '', dueDate: '' };
    this.showDialog = true;
  },

  async addTodo() {
    if (!this.newTodo.title) return;
    
    const data: any = {
      title: this.newTodo.title,
      description: this.newTodo.description,
    };
    
    if (this.newTodo.dueDate) {
      data.dueDate = new Date(this.newTodo.dueDate).toISOString();
    }
    
    const response = await fetch('/api/todo-app/todos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data),
    });
    
    if (response.ok) {
      this.showDialog = false;
      await this.loadTodos();
      await this.loadStats();
    }
  },

  async toggleTodo(todoId: string) {
    const response = await fetch(`/api/todo-app/todos/${todoId}/toggle`, {
      method: 'PATCH',
      credentials: 'include',
    });
    
    if (response.ok) {
      await this.loadTodos();
      await this.loadStats();
    }
  },

  async deleteTodo(todoId: string) {
    if (!confirm('本当に削除しますか?')) return;
    
    const response = await fetch(`/api/todo-app/todos/${todoId}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    
    if (response.ok) {
      await this.loadTodos();
      await this.loadStats();
    }
  },

  formatDate(dateStr: string): string {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('ja-JP');
  },
}));

Alpine.start();
