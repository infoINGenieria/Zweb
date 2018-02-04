import { Pipe, PipeTransform } from '@angular/core';
import { DecimalPipe } from '@angular/common';

@Pipe({
  name: 'moneda'
})
export class MonedaPipe extends DecimalPipe implements PipeTransform {

  transform(value: any, args?: any): any {
    try {
      const result = super.transform(value, '1.2-2');
      if (result === null) {
        return '#ERROR';
      }
      return `\$ ${result}`;
    } catch (ex) {
      return '#ERROR';
    }
  }

}
