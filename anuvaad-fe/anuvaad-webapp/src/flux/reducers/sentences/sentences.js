import C from '../../actions/constants';

export default function (state = {}, action) {
    switch (action.type) {
        case C.FETCH_SENTENCES:
            return action.payload;
        default:
            return state;
    }
}
