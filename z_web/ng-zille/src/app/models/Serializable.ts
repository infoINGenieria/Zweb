export class Serializable {

    fromJSON(json) {
        for (const propName of json) {
            this[propName] = json[propName];
        }
        return this;
    }
}
