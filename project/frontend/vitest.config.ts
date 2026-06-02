import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['./vitest.setup.ts'],
    include: [
      '**/*.{test,spec}.?(c|m)[jt]s?(x)',
      '../../tests/unit/logic/frontend/sys/**/*.test.ts'
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: '../../tests/unit/outputs/coverage-frontend-sys-html',
      include: ['src/sys/**/*.ts'],
      exclude: [
        'src/sys/main.ts',
        '**/*.d.ts',
        '**/*.config.ts',
        '**/types/**',
      ],
      all: true,
      lines: 100,
      functions: 100,
      branches: 100,
      statements: 100,
    },
  },
  server: {
    fs: {
      allow: ['../../tests', './src', './node_modules'],
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@sys': resolve(__dirname, './src/sys'),
    },
  },
});
