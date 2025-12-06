import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatProgressBarModule,
    MatExpansionModule,
    MatIconModule,
    MatButtonModule,
    MatChipsModule
  ],
  templateUrl: './results.component.html',
  styleUrl: './results.component.scss'
})
export class ResultsComponent {
  @Input() progress: number = 0;
  @Input() status: string = '';
  @Input() message: string = '';
  @Input() results: any = null;

  /**
   * Get severity color based on severity level
   */
  getSeverityColor(severity: string): string {
    const colors: { [key: string]: string } = {
      'CRITICAL': '#dc2626',
      'HIGH': '#ea580c',
      'MEDIUM': '#ca8a04',
      'LOW': '#2563eb'
    };
    return colors[severity] || '#6b7280';
  }

  /**
   * Get severity icon based on severity level
   */
  getSeverityIcon(severity: string): string {
    const icons: { [key: string]: string } = {
      'CRITICAL': 'error',
      'HIGH': 'warning',
      'MEDIUM': 'info',
      'LOW': 'help_outline'
    };
    return icons[severity] || 'info';
  }

  /**
   * Export results as JSON file
   */
  exportResults(): void {
    if (!this.results) return;

    const dataStr = JSON.stringify(this.results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `anomaly-analysis-${new Date().getTime()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  /**
   * Check if analysis is in progress
   */
  get isInProgress(): boolean {
    return this.status !== 'complete' && this.status !== 'error' && this.status !== '';
  }

  /**
   * Check if analysis is complete
   */
  get isComplete(): boolean {
    return this.status === 'complete';
  }

  /**
   * Check if there was an error
   */
  get isError(): boolean {
    return this.status === 'error';
  }

  /**
   * Get sorted anomalies by severity
   */
  get sortedAnomalies(): any[] {
    if (!this.results || !this.results.anomalies) return [];

    const severityOrder: { [key: string]: number } = {
      'CRITICAL': 0,
      'HIGH': 1,
      'MEDIUM': 2,
      'LOW': 3
    };

    return [...this.results.anomalies].sort((a, b) => {
      return (severityOrder[a.severity] || 999) - (severityOrder[b.severity] || 999);
    });
  }
}
