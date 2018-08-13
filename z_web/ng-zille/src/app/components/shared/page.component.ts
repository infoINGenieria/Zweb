import { Page } from '../../models/Page';
import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-pagination',
  templateUrl: './page.component.html',
  styleUrls: ['./page.component.scss']
})
export class PaginationComponent {
  @Input() page: number; // the current page
  @Input() count: number; // how many total items there are in all pages
  @Input() perPage: number; // how many items we want to show per page
  @Input() loading: boolean; // check if content is being loaded

  @Output() changePage = new EventEmitter<number>();

  constructor() {  }

  getMin(): number {
    return ((this.perPage * this.page) - this.perPage) + 1;
  }

  getMax(): number {
    let max = this.perPage * this.page;
    if (max > this.count) {
      max = this.count;
    }
    return max;
  }

  onPage(n: number): void {
    this.page = n;
    this.changePage.emit(n);
  }

  onPrev(): void {
    this.page--;
    this.changePage.emit(this.page);
  }

  onNext(): void {
    this.page++;
    this.changePage.emit(this.page);
  }

  totalPages(): number {
    return Math.ceil(this.count / this.perPage) || 0;
  }

  lastPage(): boolean {
    return this.perPage * this.page >= this.count;
  }

  getPages(): number[] {
    const pages: number[] = [];
    if (this.totalPages() <= 11) {
      for (let i = 1; i <= this.totalPages(); i++) {
        pages.push(i);
      }
    } else {
      // del 1 hasta la pagina actual
      for (let i = 1; i <= this.page; i++) {
        if (i === 1) {
          pages.push(i);
        } else if (i >= this.page - 4) {
          pages.push(i);
        }
      }
      // numero despues de la página actual
      // añado los restantes para llegar a un total de 11
      for (let i = this.page + 1; i < this.page + pages.length; i++) {
        if (i < this.totalPages()) {
          pages.push(i);
        }
      }
      pages.push(this.totalPages());
    }
    pages.sort((a, b) => a - b);
    return pages;
  }

  // hasPrevious(): boolean {
  //   return this.page.pageNumber > 1;
  // }

  // hasNext(): boolean { return this.page.pageNumber < this.page.totalPages; }

  // nextPage() {
  //   this.page.pageNumber ++;
  //   if (this.page.pageNumber > this.page.totalPages) {
  //     this.page.pageNumber = this.page.totalPages;
  //   } else {
  //     this.pageChanged.emit(this.page.pageNumber);
  //   }
  // }

  // previousPage() {
  //   this.page.pageNumber --;
  //   if (this.page.pageNumber < 1) {
  //     this.page.pageNumber = 1;
  //   } else {
  //     this.pageChanged.emit(this.page.pageNumber);
  //   }
  // }

}
