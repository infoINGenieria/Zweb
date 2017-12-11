import { Pipe, PipeTransform } from '@angular/core';
import { DecimalPipe } from '@angular/common';

@Pipe({
  name: 'porciento'
})
export class PorcientoPipe extends DecimalPipe implements PipeTransform {

  transform(value: any, args?: any): any {
    try {
      const result = super.transform(value, '1.1-1');
      return `${result} %`;
    } catch (ex) {
      return '#ERROR';
    }
  }

}
