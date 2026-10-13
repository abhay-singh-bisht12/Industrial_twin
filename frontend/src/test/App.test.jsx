import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import App from '../App';

// Mock Recharts and Three.js for Vitest DOM testing
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div>{children}</div>,
  LineChart: ({ children }) => <div>{children}</div>,
  Line: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Tooltip: () => <div />,
  CartesianGrid: () => <div />
}));

describe('IndustrialTwin Digital Twin Frontend', () => {
  it('renders Header title and Digital Twin dashboard layout', () => {
    render(<App />);
    expect(screen.getByText('IndustrialTwin')).toBeInTheDocument();
    expect(screen.getByText('MACHINE HEALTH INDEX')).toBeInTheDocument();
    expect(screen.getByText('FAULT INJECTION CONTROL PANEL')).toBeInTheDocument();
  });

  it('displays telemetry card headers', () => {
    render(<App />);
    expect(screen.getByText('Temperature')).toBeInTheDocument();
    expect(screen.getByText('Vibration RMS')).toBeInTheDocument();
    expect(screen.getByText('Shaft Speed')).toBeInTheDocument();
    expect(screen.getByText('Phase Current')).toBeInTheDocument();
  });

  it('renders fault injection state buttons', () => {
    render(<App />);
    expect(screen.getByText('✅ NORMAL')).toBeInTheDocument();
    expect(screen.getByText('🔥 OVERHEATING')).toBeInTheDocument();
    expect(screen.getByText('⚙️ BEARING WEAR')).toBeInTheDocument();
    expect(screen.getByText('⚡ ELEC FAULT')).toBeInTheDocument();
  });
});
