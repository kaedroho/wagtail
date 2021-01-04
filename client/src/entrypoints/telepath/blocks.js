/* eslint-disable indent, vars-on-top, no-warning-comments, max-len */

/* global $ */

function initBlockWidget(id) {
    /*
    Initialises the top-level element of a BlockWidget
    (i.e. the form widget for a StreamField).
    Receives the ID of a DOM element with the attributes:
        data-block: JSON-encoded block definition to be passed to telepath.unpack
            to obtain a Javascript representation of the block
            (i.e. an instance of one of the Block classes below)
        data-value: JSON-encoded value for this block
    */

    var body = document.getElementById(id);

    // unpack the block definition and value
    var blockDefData = JSON.parse(body.dataset.block);
    var blockDef = window.telepath.unpack(blockDefData);
    var blockValue = JSON.parse(body.dataset.value);

    // replace the 'body' element with the unpopulated HTML structure for the block
    var block = blockDef.render(body, id);
    // populate the block HTML with the value
    block.setState(blockValue);
}
window.initBlockWidget = initBlockWidget;

class FieldBlock {
    constructor(name, widget, meta) {
        this.name = name;
        this.widget = window.telepath.unpack(widget);
        this.meta = meta;
    }

    render(placeholder, prefix) {
        const container = document.createElement('div');
        container.innerHTML = `
            <div class="field-content">
                <div class="input">
                    <div data-streamfield-widget></div>
                    <span></span>
                </div>
            </div>
        `;
        placeholder.replaceWith(container);

        const widgetElement = container.querySelector('[data-streamfield-widget]');
        const boundWidget = this.widget.render(widgetElement, prefix, prefix);
        return {
            type: this.name,
            setState(state) {
                boundWidget.setState(state);
            },
            getState() {
                boundWidget.getState();
            },
            getValue() {
                boundWidget.getValue();
            },
        };
    }
}
window.telepath.register('wagtail.blocks.FieldBlock', FieldBlock);


class StructBlock {
    constructor(name, childBlocks, meta) {
        this.name = name;
        this.childBlocks = childBlocks.map((child) => window.telepath.unpack(child));
        this.meta = meta;
    }

    render(placeholder, prefix) {
        const container = document.createElement('div');
        container.setAttribute('class', this.meta.classname);
        placeholder.replaceWith(container);

        const boundBlocks = {};
        this.childBlocks.forEach(childBlock => {
            const childContainer = document.createElement('div');
            childContainer.classList.add('field');
            childContainer.innerHTML = `
                <label class="field__label">${childBlock.meta.label}</label>
                <div data-streamfield-block></div>
            `;
            container.appendChild(childContainer);

            const childBlockElement = childContainer.querySelector('[data-streamfield-block]');
            const boundBlock = childBlock.render(childBlockElement, prefix + '-' + childBlock.name);

            boundBlocks[childBlock.name] = boundBlock;
        });

        return {
            type: this.name,
            setState(state) {
                // eslint-disable-next-line guard-for-in, no-restricted-syntax, no-native-reassign
                for (name in state) {
                    boundBlocks[name].setState(state[name]);
                }
            },
            getState() {
                var state = {};
                // eslint-disable-next-line guard-for-in, no-restricted-syntax, no-native-reassign
                for (name in boundBlocks) {
                    state[name] = boundBlocks[name].getState();
                }
                return state;
            },
            getValue() {
                var value = {};
                // eslint-disable-next-line guard-for-in, no-restricted-syntax, no-native-reassign
                for (name in boundBlocks) {
                    value[name] = boundBlocks[name].getValue();
                }
                return value;
            },
        };
    }
}
window.telepath.register('wagtail.blocks.StructBlock', StructBlock);


class ListBlock {
    constructor(name, childBlock, meta) {
        this.name = name;
        this.childBlock = window.telepath.unpack(childBlock);
        this.meta = meta;
    }

    render(placeholder, prefix) {
        const container = document.createElement('div');
        container.setAttribute('class', `c-sf-container ${this.meta.classname || ''}`);
        container.innerHTML = `
            <input type="hidden" name="${prefix}-count" data-streamfield-list-count value="0">
            <div data-streamfield-list-container></div>
            <button type="button" title="Add" data-streamfield-list-add class="c-sf-add-button c-sf-add-button--visible"><i aria-hidden="true">+</i></button>
        `;
        placeholder.replaceWith(container);

        let boundBlocks = [];
        const countInput = container.querySelector('[data-streamfield-list-count]');
        const listContainer = container.querySelector('[data-streamfield-list-container]');

        var self = this;

        return {
            type: this.name,
            setState(values) {
                countInput.val(values.length);
                boundBlocks = [];
                listContainer.empty();
                values.forEach((val, index) => {
                    const childPrefix = prefix + '-' + index;

                    const childContainer = document.createElement('div');
                    childContainer.id = `${childPrefix}-container`;
                    childContainer.setAttribute('aria-hidden', 'false');
                    childContainer.innerHTML = `
                        <input type="hidden" id="${childPrefix}-deleted" name="${childPrefix}-deleted" value="">
                        <input type="hidden" id="${childPrefix}-order" name="${childPrefix}-order" value="${index}">
                        <div>
                            <div class="c-sf-container__block-container">
                                <div class="c-sf-block">
                                    <div class="c-sf-block__header">
                                        <span class="c-sf-block__header__icon">
                                            <i class="icon icon-${self.childBlock.meta.icon}"></i>
                                        </span>
                                        <h3 class="c-sf-block__header__title"></h3>
                                        <div class="c-sf-block__actions">
                                            <span class="c-sf-block__type"></span>
                                            <button type="button" id="${childPrefix}-moveup" class="c-sf-block__actions__single" title="{% trans 'Move up' %}">
                                            <i class="icon icon-arrow-up" aria-hidden="true"></i>
                                        </button>
                                        <button type="button" id="${childPrefix}-movedown" class="c-sf-block__actions__single" title="{% trans 'Move down' %}">
                                            <i class="icon icon-arrow-down" aria-hidden="true"></i>
                                        </button>
                                        <button type="button" id="${childPrefix}-delete" class="c-sf-block__actions__single" title="{% trans 'Delete' %}">
                                            <i class="icon icon-bin" aria-hidden="true"></i>
                                        </button>

                                        </div>
                                    </div>
                                    <div class="c-sf-block__content" aria-hidden="false">
                                        <div class="c-sf-block__content-inner">
                                            <div data-streamfield-block></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    listContainer.appendChild(childContainer);

                    const childBlockElement = childContainer.querySelector('[data-streamfield-block]');
                    const boundBlock = self.childBlock.render(childBlockElement, childPrefix + '-value');
                    boundBlock.setState(val);
                    boundBlocks.push(boundBlock);
                });
            },
            getState() {
                return boundBlocks.map((boundBlock) => boundBlock.getState());
            },
            getValue() {
                return boundBlocks.map((boundBlock) => boundBlock.getValue());
            },
        };
    }
}
window.telepath.register('wagtail.blocks.ListBlock', ListBlock);


class StreamBlock {
    constructor(name, childBlocks, meta) {
        this.name = name;
        this.childBlocks = childBlocks.map((child) => window.telepath.unpack(child));
        this.childBlocksByName = {};
        for (var i = 0; i < this.childBlocks.length; i++) {
            var block = this.childBlocks[i];
            this.childBlocksByName[block.name] = block;
        }
        this.meta = meta;
    }

    render(placeholder, prefix) {
        const container = document.createElement('div');
        container.setAttribute('class', `c-sf-container ${this.meta.classname || ''}`);
        container.innerHTML = `
            <input type="hidden" name="${prefix}-count" data-streamfield-stream-count value="0">
            <div data-streamfield-stream-container></div>
        `;
        placeholder.replaceWith(container);

        let boundBlocks = [];
        const countInput = container.querySelector('[data-streamfield-stream-count]');
        const streamContainer = container.querySelector('[data-streamfield-stream-container]');

        const self = this;

        return {
            type: this.name,
            setState(values) {
                countInput.val(values.length);
                streamContainer.empty();
                boundBlocks = [];
                values.forEach((blockData, index) => {
                    const blockType = blockData.type;
                    const block = self.childBlocksByName[blockType];

                    const childPrefix = prefix + '-' + index;

                    const childContainer = document.createElement('div');
                    childContainer.id = `${childPrefix}-container`;
                    childContainer.setAttribute('aria-hidden', 'false');
                    childContainer.innerHTML = `
                        <input type="hidden" name="${childPrefix}-deleted" value="">
                        <input type="hidden" name="${childPrefix}-order" value="${index}">
                        <input type="hidden" name="${childPrefix}-type" value="${blockType}">
                        <input type="hidden" name="${childPrefix}-id" value="${blockData.id || ''}">

                        <div>
                            <div class="c-sf-container__block-container">
                                <div class="c-sf-block">
                                    <div class="c-sf-block__header">
                                        <span class="c-sf-block__header__icon">
                                            <i class="icon icon-${block.meta.icon}"></i>
                                        </span>
                                        <h3 class="c-sf-block__header__title"></h3>
                                        <div class="c-sf-block__actions">
                                            <span class="c-sf-block__type">${block.meta.label}</span>
                                            <button type="button" class="c-sf-block__actions__single" title="{% trans 'Move up' %}">
                                                <i class="icon icon-arrow-up" aria-hidden="true"></i>
                                            </button>
                                            <button type="button" class="c-sf-block__actions__single" title="{% trans 'Move down' %}">
                                                <i class="icon icon-arrow-down" aria-hidden="true"></i>
                                            </button>
                                            <button type="button" class="c-sf-block__actions__single" title="{% trans 'Delete' %}">
                                                <i class="icon icon-bin" aria-hidden="true"></i>
                                            </button>

                                        </div>
                                    </div>
                                    <div class="c-sf-block__content" aria-hidden="false">
                                        <div class="c-sf-block__content-inner">
                                            <div data-streamfield-block></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    streamContainer.appendChild(childContainer);

                    const childBlockElement = childContainer.querySelector('[data-streamfield-block]');
                    const boundBlock = block.render(childBlockElement, childPrefix + '-value');
                    boundBlock.setState(blockData.value);
                    boundBlocks.push(boundBlock);
                });
            },
            getState() {
                return boundBlocks.map((boundBlock) => ({
                        type: boundBlock.type,
                        val: boundBlock.getState(),
                        id: null, /* TODO: add this */
                    }));
            },
            getValue() {
                return boundBlocks.map((boundBlock) => ({
                        type: boundBlock.type,
                        val: boundBlock.getValue(),
                        id: null, /* TODO: add this */
                    }));
            },
        };
    }
}
window.telepath.register('wagtail.blocks.StreamBlock', StreamBlock);
